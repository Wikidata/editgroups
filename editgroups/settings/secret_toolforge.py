import os
from .common import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'insert_a_random_hash_here'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 's1234__editgroups', # adapt to the database you created
        'HOST': 'tools.db.svc.eqiad.wmflabs',
        'OPTIONS': {
           'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           'charset': 'utf8mb4',
           'read_default_file': os.path.expanduser("~/replica.my.cnf")
        },
    }
}

# Adapt those to the credentials you got
SOCIAL_AUTH_MEDIAWIKI_KEY = ''
SOCIAL_AUTH_MEDIAWIKI_SECRET = ''
SOCIAL_AUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'https://editgroups.toolforge.org/oauth/complete/mediawiki/'

# Redis (if you use it)
REDIS_HOST = 'tools-redis'
REDIS_PORT = 6379
REDIS_DB = 3
REDIS_PASSWORD = ''
REDIS_KEY_PREFIX = 'editgroups_'

