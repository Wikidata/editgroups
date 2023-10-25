from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import json
import random
import requests
from requests_oauthlib import OAuth1
from cached_property import cached_property

from store.models import NEW_PAGE_CHANGETYPES
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

    def comment_with_stamp(self):
        return (self.comment +
                settings.REVERT_COMMENT_STAMP.format(self.uid))

    def undo_summary(self, edit):
        prefix = '/* undo:0||{}|{} */ '.format(edit.newrevid, edit.user)
        return (prefix + self.comment_with_stamp())

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
        r = requests.get(settings.MEDIAWIKI_API_ENDPOINT, params={
            'action':'query',
            'meta':'tokens',
            'format': 'json',
        }, auth=auth)
        r.raise_for_status()
        token = r.json()['query']['tokens']['csrftoken']

        if edit.oldrevid:
            # Undo the edit
            data = {
                'action':'edit',
                'title': edit.title,
                'undo': edit.newrevid,
                'summary': self.undo_summary(edit),
                'format': 'json',
                'token': token,
                'watchlist': 'nochange',
            }
        elif edit.changetype in NEW_PAGE_CHANGETYPES:
            # Delete the page
            data = {
                'action': 'delete',
                'title': edit.title,
                'reason': self.comment_with_stamp(),
                'token': token,
                'format': 'json',
                'watchlist': 'nochange',
            }
        elif edit.changetype == 'delete':
            # Restore the page
            data = {
                'action': 'undelete',
                'title': edit.title,
                'reason': self.comment_with_stamp(),
                'token': token,
                'format': 'json',
                'watchlist': 'nochange',
            }

        r = requests.post(settings.MEDIAWIKI_API_ENDPOINT,
                data=data, auth=auth)

        #r.raise_for_status()



