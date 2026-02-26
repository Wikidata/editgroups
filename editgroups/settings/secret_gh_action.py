
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20oj&tj8uaruseitlrise,tries,uirsetur36746209etus7e'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 'MARIADB_PORT',
        'NAME': 'editgroups',
        'USER': 'root',
        'PASSWORD': 'editgroups',
        'OPTIONS': {
           'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           'charset': 'utf8mb4',
        },
    }
}

# OAuth for Wikidata
SOCIAL_AUTH_MEDIAWIKI_KEY = 'FILL_THIS'
SOCIAL_AUTH_MEDIAWIKI_SECRET = 'FILL_THIS'
SOCIAL_AUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'https://tools.wmflabs.org/editgroups/oauth/complete/mediawiki/'


# Redis (if you use it)
REDIS_HOST = 'localhost'
REDIS_PORT = REDIS_REAL_PORT
REDIS_DB = 0
REDIS_PASSWORD = ''
REDIS_KEY_PREFIX = 'editgroups_'


