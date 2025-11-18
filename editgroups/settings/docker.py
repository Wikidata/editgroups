from .common import *

DEBUG = True
ALLOWED_HOSTS = ['*']

SECRET_KEY = '20oj&tj8uaruseitlrise,tries,uirsetur36746209etus7e'

DATABASES = {
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

SOCIAL_AUTH_MEDIAWIKI_KEY = 'your_mediawiki_key'
SOCIAL_AUTH_MEDIAWIKI_SECRET = 'your_mediawiki_secret'
SOCIAL_AUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'http://localhost:8000/oauth/complete/mediawiki/'

REDIS_HOST = 'redis'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''
REDIS_KEY_PREFIX = 'editgroups_'
