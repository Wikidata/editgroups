from .common import *

DEBUG = False
ALLOWED_HOSTS = ['tools.wmflabs.org']

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/editgroups/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': 'tools-redis:6379',
        'OPTIONS': {
            'DB': 2,
        },
    },
}

LOGIN_URL = '/editgroups/oauth/login/mediawiki/'
