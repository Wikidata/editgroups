import os

SECRET_KEY = 'django-insecure-0ldt)=t=w(%l)7b28n=x!#9ciei^yuox3204(#(r!-fh^59+a-'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'mariadb',
        'NAME': os.getenv("DB_NAME"),
        'PASSWORD': os.getenv("DB_PASSWORD"),
        'OPTIONS': {
           'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           'charset': 'utf8mb4',
        },
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
