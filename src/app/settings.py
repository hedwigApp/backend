import logging
import os
from datetime import timedelta

import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

root = environ.Path(__file__) - 3        # three folder back (/a/b/c/ - 3 = /)
env = environ.Env(DEBUG=(bool, False),)  # set default values and casting
environ.Env.read_env()                   # reading .env file

DEBUG = env('DEBUG')
CI = env('CI', cast=bool, default=False)

SITE_ROOT = root()

USE_L10N = True
USE_i18N = True
USE_TZ = True


AUTH_USER_MODEL = 'a12n.User'

# SECURITY WARNING: keep the secret key used in production secret!

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = [
    r'.*localhost.*',
    r'.*127.0.0.1.*',
]

ABSOLUTE_HOST = env('ABSOLUTE_HOST')
ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'localhost:8000',
]

if DEBUG:
    ALLOWED_HOSTS = ['*']


DATABASES = {
    'default': env.db(),    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
}

CONN_MAX_AGE = 300  # https://docs.djangoproject.com/en/2.0/ref/databases/#persistent-connections

TEST_RUNNER = 'app.test.disable_test_command_runner.DisableTestCommandRunner'


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'behaviors.apps.BehaviorsConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'django.contrib.postgres',

    'app',
    'a12n',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
        'nplusone.ext.django',
    ]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.TokenAuthMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
]


if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        'querycount.middleware.QueryCountMiddleware',
    ]

    MIDDLEWARE = ['nplusone.ext.django.NPlusOneMiddleware', ] + MIDDLEWARE


if DEBUG:
    # Logging N+1 requests:
    NPLUSONE_RAISE = True  # comment out if you want to allow N+1 requests
    NPLUSONE_LOGGER = logging.getLogger('django')
    NPLUSONE_LOG_LEVEL = logging.WARN

ROOT_URLCONF = 'app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.DjangoModelPermissions',
        'app.permissions.DjangoModelStrictPermissions',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'app.renderers.AppJSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_PAGINATION_CLASS': 'app.pagination.AppPagination',
    'PAGE_SIZE': 20,
    'TIME_FORMAT': '%H:%M',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'ROTATE_REFRESH_TOKENS': True,
\
}

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    # 'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',

    'debug_toolbar.panels.profiling.ProfilingPanel',

    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

WSGI_APPLICATION = 'app.wsgi.application'

public_root = root.path('public/')

MEDIA_URL = env('MEDIA_URL')
MEDIA_ROOT = env('MEDIA_ROOT')

STATIC_URL = env('STATIC_URL')
STATIC_ROOT = env('STATIC_ROOT')

SECRET_KEY = env('SECRET_KEY')

INTERNAL_IPS = [
    '127.0.0.1',
    '::1',
]

CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    },
}

CELERY_ALWAYS_EAGER = env('CELERY_ALWAYS_EAGER', cast=bool, default=DEBUG)

CELERY_TIMEZONE = env('TIME_ZONE')
CELERY_ENABLE_UTC = False
CELERY_ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': env('REDIS'),
        'default_timeout': 10 * 60,
        'blocking': CELERY_ALWAYS_EAGER,
    },
}

BROKER_URL = env('CELERY_BACKEND')

CELERY_ROUTES = {}

CELERYBEAT_SCHEDULE = {}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env('TIME_ZONE')
