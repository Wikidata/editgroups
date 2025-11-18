import os
import sys
from types import ModuleType

secret = ModuleType('editgroups.settings.secret')
secret.SECRET_KEY = '20oj&tj8uaruseitlrise,tries,uirsetur36746209etus7e'
secret.DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'editgroups',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
        'DISABLE_SERVER_SIDE_CURSORS': False,
    }
}
secret.SOCIAL_AUTH_MEDIAWIKI_KEY = 'your_mediawiki_key'
secret.SOCIAL_AUTH_MEDIAWIKI_SECRET = 'your_mediawiki_secret'
secret.SOCIAL_AUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
secret.SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'http://localhost:8000/oauth/complete/mediawiki/'
secret.REDIS_HOST = 'redis'
secret.REDIS_PORT = 6379
secret.REDIS_DB = 0
secret.REDIS_PASSWORD = ''
secret.REDIS_KEY_PREFIX = 'editgroups_'

sys.modules['editgroups.settings.secret'] = secret

from .common import *

DEBUG = True
ALLOWED_HOSTS = ['*']
BASE_DIR = os.path.dirname(os.path.dirname(__file__))