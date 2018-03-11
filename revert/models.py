from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import json
import random
import requests
from requests_oauthlib import OAuth1
from cached_property import cached_property

from store.models import Batch
from store.models import Edit

def generate_uid():
    uid_length = 7
    return ('%0'+str(uid_length)+'x') % random.randrange(16**uid_length)

class RevertTask(models.Model):
    """
    Represents the task of undoing a batch
    """
    uid = models.CharField(max_length=32, default=generate_uid)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='revert_tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    cancel = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return 'reverting '+str(self.batch)

    def summary(self, edit):
        prefix = '/* undo:0||{}|{} */ '.format(edit.newrevid, edit.user)
        return (prefix + self.comment +
                ' ([[:toollabs:editgroups/b/EG/{}|details]])'.format(self.uid))

    @cached_property
    def oauth_tokens(self):
        """
        Returns a dictionary containing the OAuth
        tokens required to execute the task.
        Raises various exceptions if the task is
        canceled, or OAuth tokens could not be found.
        """
        if self.cancel:
             raise ValueError('Task was canceled.')
        socialauth = self.user.social_auth.get()
        dct = socialauth.extra_data
        return dct['access_token']

    def revert_edit(self, edit):
        """
        Reverts the given edit via the MediaWiki API.
        """
        auth = OAuth1(
            settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
            settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
            self.oauth_tokens['oauth_token'],
            self.oauth_tokens['oauth_token_secret'])

        # Get token
        r = requests.get('https://www.wikidata.org/w/api.php', params={
        'action':'query',
        'meta':'tokens',
            'format': 'json',
        }, auth=auth)
        print('#### GET TOKEN')
        print(r.url)
        print(r.text)
        r.raise_for_status()
        token = r.json()['query']['tokens']['csrftoken']

        # Undo the edit
        data = {
            'action':'edit',
            'title': edit.title,
            'undo': edit.newrevid,
            'summary': self.summary(edit),
            'format': 'json',
            'token': token,
            'watchlist': 'nochange',
        }
        r = requests.post('https://www.wikidata.org/w/api.php',
                data=data, auth=auth)

        print('#### UNDO EDIT')
        print(data)
        print(r.text)
        #r.raise_for_status()


