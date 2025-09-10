"""
Django settings for editgroups project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

try:
    from .secret import DATABASES
    from .secret import REDIS_DB
    from .secret import REDIS_HOST
    from .secret import REDIS_PASSWORD
    from .secret import REDIS_PORT
    from .secret import REDIS_KEY_PREFIX
    from .secret import SECRET_KEY
    from .secret import SOCIAL_AUTH_MEDIAWIKI_KEY
    from .secret import SOCIAL_AUTH_MEDIAWIKI_SECRET
    from .secret import SOCIAL_AUTH_MEDIAWIKI_URL
    from .secret import SOCIAL_AUTH_MEDIAWIKI_CALLBACK
except ImportError as e:
    raise RuntimeError(
        'Secret file is missing, did you forget to add a secret.py in your settings folder?')



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!

TEMPLATE_DEBUG = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'django_filters',
    'rest_framework',
    'store',
    'revert',
    'tagging',
    'django_extensions',
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]


ROOT_URLCONF = 'editgroups.urls'

TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                os.path.join(BASE_DIR, 'templates')
            ],
            'OPTIONS': {
                'loaders': (
                    ('django.template.loaders.cached.Loader', (
                        'django.template.loaders.filesystem.Loader',
                        'django.template.loaders.app_directories.Loader',
                    )),
                ),
                'context_processors': (
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.template.context_processors.request",
                    "social_django.context_processors.backends",
                    "social_django.context_processors.login_redirect",
                    "tagging.filters.context_processor",
                    "editgroups.context_processors.mediawiki_site_settings",
                ),
                'debug': True
            }
        }
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.TemplateHTMLRenderer',
        'rest_framework.renderers.JSONRenderer',
     ),
    'DEFAULT_PAGINATION_CLASS': 'store.pagination.PaginationWithoutCounts',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'REST_FRAMEWORK':{
        'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)
    }
}

WSGI_APPLICATION = 'editgroups.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
AUTHENTICATION_BACKENDS = (
    'editgroups.oauth.CustomMediaWiki',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/oauth/login/mediawiki/'
LOGIN_REDIRECT_URL = 'list-batches'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Temporary date format before we enable localization
# TODO: remove this, set USE_L10N = True, add middleware, enable localization
# with middleware  'django.middleware.locale.LocaleMiddleware',
DATETIME_FORMAT = 'H:i, d F Y (e)'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "../static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Taken from https://gist.github.com/DamianZaremba/e6d65a200f7c451db80939e7e9e4f2c8
# Shrink specific columns down, so the key combination for the constraints
# aren't larger than the max legnth, when not using innodb_large_prefix.
# Length may require tweaking depending on application requirements
SOCIAL_AUTH_UID_LENGTH = 190
SOCIAL_AUTH_NONCE_SERVER_URL_LENGTH = 190
SOCIAL_AUTH_ASSOCIATION_SERVER_URL_LENGTH = 190
SOCIAL_AUTH_ASSOCIATION_HANDLE_LENGTH = 190
SOCIAL_AUTH_EMAIL_LENGTH = 190
SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['groups']

MEDIAWIKI_API_ENDPOINT = 'https://www.wikidata.org/w/api.php'
MEDIAWIKI_BASE_URL = 'https://www.wikidata.org/wiki/'
MEDIAWIKI_INDEX_ENDPOINT = 'https://www.wikidata.org/w/index.php'
PROPERTY_BASE_URL = MEDIAWIKI_BASE_URL + 'Property:'
USER_BASE_URL = MEDIAWIKI_BASE_URL + 'User:'
USER_TALK_BASE_URL = MEDIAWIKI_BASE_URL + 'User_talk:'
CONTRIBUTIONS_BASE_URL = MEDIAWIKI_BASE_URL + 'Special:Contributions/'
WIKI_CODENAME = 'wikidatawiki'
USER_DOCS_HOMEPAGE = 'https://www.wikidata.org/wiki/Wikidata:Edit_groups'
MEDIAWIKI_NAME = 'Wikidata'
DISCUSS_PAGE_PREFIX = 'Wikidata:Edit_groups/'
DISCUSS_PAGE_PRELOAD = 'Wikidata:Edit_groups/Preload'
REVERT_PAGE = 'Wikidata:Requests_for_deletions'
REVERT_PRELOAD = 'Wikidata:Edit_groups/Revert'
WATCHED_NAMESPACES = [0, 120, 122, 146, 640, 6]

WIKILINK_BATCH_PREFIX = ':toollabs:editgroups/b/'
REVERT_COMMENT_STAMP = ' ([[:toollabs:editgroups/b/EG/{}|details]])'

### Celery config ###
# Celery runs asynchronous tasks such as metadata harvesting or
# complex updates.
# To communicate with it, we need a "broker".
# This is an example broker with Redis
# (with settings configured in your secret.py)
REDIS_URL = ':%s@%s:%s/%d' % (
        REDIS_PASSWORD,
        REDIS_HOST,
        REDIS_PORT,
        REDIS_DB)
BROKER_URL = 'redis://'+REDIS_URL
CELERY_BROKER_URL = BROKER_URL
# We also use Redis as result backend.
CELERY_RESULT_BACKEND = BROKER_URL

CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
CELERY_IMPORTS = ['revert.tasks', 'tagging.tasks' ]

# Batch inspection
BATCH_INSPECTION_LOOKBEHIND = timedelta(minutes=30)
BATCH_INSPECTION_DELAY = timedelta(minutes=10)

# Batch archival
BATCH_ARCHIVAL_DELAY = timedelta(days=365) # Batches older than that are archived
EDITS_KEPT_AFTER_ARCHIVAL = 10 # Only that many edits will be kept in archived batches
BATCH_ARCHIVAL_PERIODICITY = timedelta(days=1)

CELERYBEAT_SCHEDULE = {
    'inspect_batches': {
        'task': 'inspect_batches',
        'schedule': BATCH_INSPECTION_DELAY,
    },
    'archive_batches': {
        'task': 'archive_batches',
        'schedule': BATCH_ARCHIVAL_PERIODICITY,
    }
}

USER_AGENT = "EditGroups (https://www.wikidata.org/wiki/Wikidata:Edit_groups)"
