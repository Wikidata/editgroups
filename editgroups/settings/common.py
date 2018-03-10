"""
Django settings for editgroups project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

try:
    from .secret import DATABASES
    from .secret import REDIS_DB
    from .secret import REDIS_HOST
    from .secret import REDIS_PASSWORD
    from .secret import REDIS_PORT
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
    'rest_framework',
    'store',
    'revert',
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
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.template.context_processors.static",
                    "django.template.context_processors.tz",
                    "django.template.context_processors.request",
                    "social_django.context_processors.backends",
                    "social_django.context_processors.login_redirect",
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
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
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
    'social_core.backends.mediawiki.MediaWiki',
    'django.contrib.auth.backends.ModelBackend',
)

LOGIN_URL = '/oauth/login/mediawiki/'
LOGIN_REDIRECT_URL = 'list-batches'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


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
