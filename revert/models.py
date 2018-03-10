from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from requests_oauthlib import OAuth1
import json
from cached_property import cached_property

from store.models import Batch
from store.models import Edit

class RevertTask(models.Model):
    """
    Represents the task of undoing a batch
    """
    uid = models.CharField(max_length=32)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    cancel = models.BooleanField(default=False)

    @property
    def summary(self):
        return (self.comment +
                ' ([[:toollabs:editgroups/b/EG/{}|details]])'.format(self.uid))

    @cached_property
    def oauth_tokens(self):
        """
        Returns a dictionary containing the OAuth 
        tokens required to execute the task.
        Raises various exceptions if the task is
        canceled, or OAuth tokens could not be found.
        """
        if self.canceled:
             raise ValueError('Task was canceled.')
        socialauth = t.user.social_auth.get()
        dct = json.loads(socialauth.extra_data)
        return dct['access_token']        

    def revert_edit(self, edit):
        """
        Reverts the given edit via the MediaWiki API.
        """
        auth = OAuth1(
            settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
            settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
            self.oauth_tokens['oauth_token'],
            self.oauth_tokens['oauth_secret_token'])

        # Get token
        r = requests.get('https://www.wikidata.org/w/api.php', params={
        'action':'query',
        'meta':'tokens',
            'format': 'json',
        }, auth=auth)
        r.raise_for_status()
        token = r.json()['query']['tokens']['csrftoken']

        # Undo the edit
        r = requests.post('https://www.wikidata.org/w/api.php', data={
            'action':'edit',
            'title': edit.title,
            'undo': edit.newrevid,
            'summary': self.summary,
            'format': 'json',
            'token': token,
            'watchlist': 'nochange',
        }, auth=auth)
        r.raise_for_status()


