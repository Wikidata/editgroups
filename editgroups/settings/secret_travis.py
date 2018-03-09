
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20oj&tj8uaruseitlrise,tries,uirsetur36746209etus7e'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'editgroups',
        'USER': 'travis',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

# OAuth for Wikidata
SOCIAL_AUTH_MEDIAWIKI_KEY = 'FILL_THIS'
SOCIAL_AUTH_MEDIAWIKI_SECRET = 'FILL_THIS'
SOCIAL_AUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
SOCIAL_AUTH_MEDIAWIKI_CALLBACK = 'https://tools.wmflabs.org/editgroups/oauth/complete/mediawiki/'


# Redis (if you use it)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''


