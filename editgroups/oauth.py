"""
Defines a custom backend to retrieve user rights when logging in.
"""

import requests
from social_core.backends.mediawiki import MediaWiki
from django.conf import settings
from requests_oauthlib import OAuth1

class CustomMediaWiki(MediaWiki):
    def extra_data(self, user, uid, response, details=None, *args, **kwargs):
        data = super(MediaWiki, self).extra_data(user, uid, response, details, *args, **kwargs)
        access_token = data['access_token']
        auth = OAuth1(
            settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
            settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
            access_token['oauth_token'],
            access_token['oauth_token_secret'])

        r = requests.get(settings.MEDIAWIKI_API_ENDPOINT,
            {'action':'query',
             'meta':'userinfo',
             'uiprop':'rights|ratelimits|blockinfo'
            }, auth=auth)
        data['userinfo'] = r.json()['query']['userinfo']
        return data

