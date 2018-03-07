
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '20oj&tj8uaruseitlrise,tries,uirsetur36746209etus7e'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'batchrevert',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
    }
}

# Redis (if you use it)
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = ''


