from __future__ import annotations

import logging
from pathlib import Path
from urllib.parse import urljoin

from configurations import Configuration

from django.utils.functional import cached_property

from netflix.logging import LoggerDescriptor

from .values import from_environ


class Base(Configuration):
    log = LoggerDescriptor(__name__)

    PROJECT_NAME = 'NETFLIX'
    PROJECT_BASE_URL = from_environ('http://localhost')
    # Идентификатор инсталляции, произвольная строка (e.g., 'stage', 'prod', 'production').
    PROJECT_ENVIRONMENT = from_environ('unknown')
    # Исправлять относительные MEDIA_URL и STATIC_URL на абсолютные, используя PROJECT_BASE_URL
    FIX_RELATIVE_URLS = from_environ(True)

    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    ALLOWED_HOSTS = []
    CSRF_TRUSTED_ORIGINS = []

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = from_environ(name="DJANGO_SECRET_KEY")

    # Application definition
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        'django_extensions',
        'django_filters',
        'rest_framework',
        'rest_framework.authtoken',
        'drf_spectacular',

        'netflix.movies.apps.MoviesConfig',
    ]

    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

    ROOT_URLCONF = 'netflix.urls'
    WSGI_APPLICATION = 'netflix.wsgi.application'
    DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': from_environ(name='DB_NAME'),
            'USER': from_environ(name='DB_USER'),
            'PASSWORD': from_environ(name='DB_PASSWORD'),
            'HOST': from_environ(name='DB_HOST'),
            'PORT': from_environ(name='DB_PORT', type=int),
        },
    }

    # Password validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Internationalization
    LANGUAGE_CODE = 'ru-ru'
    TIME_ZONE = 'Europe/Moscow'
    USE_I18N = True
    USE_TZ = True

    # STATIC
    STATIC_URL = from_environ('/staticfiles/')
    STATIC_ROOT = PROJECT_ROOT / 'staticfiles'

    # MEDIA
    MEDIA_URL = from_environ('/media/')
    MEDIA_ROOT = PROJECT_ROOT / 'media'

    # TEMPLATES
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

    # AUTHENTICATION
    LOGIN_URL = '/'
    LOGIN_REDIRECT_URL = '/'
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
    ]

    # EMAIL
    DEFAULT_FROM_EMAIL = 'notify@netflix.ru'
    DEFAULT_SENDER = f'{PROJECT_NAME} <{DEFAULT_FROM_EMAIL}>'
    DEFAULT_TO_EMAIL = []

    @cached_property
    def LOGGING(self):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '[ %(levelname)-7s ] %(asctime)s %(name)s: %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        }

    # REST_FRAMEWORK
    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': ['rest_framework.parsers.JSONParser'],
        'DEFAULT_RENDERER_CLASSES': ['rest_framework.renderers.JSONRenderer'],
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'netflix.api.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    }

    @cached_property
    def SPECTACULAR_SETTINGS(self):
        return {
            'TITLE': f'{self.PROJECT_NAME} API',
            'VERSION': None,
            'SCHEMA_PATH_PREFIX': r'/api/v[0-9]+/',
            'SCHEMA_PATH_PREFIX_TRIM': True,
            'SERVE_AUTHENTICATION': ['rest_framework.authentication.SessionAuthentication'],
            'SERVE_PERMISSIONS': ['netflix.api.permissions.IsSuperUser'],
            'SERVERS': [{'url': f'{self.PROJECT_BASE_URL}/api/v1'}],
        }

    # FILES
    FILE_UPLOAD_PERMISSIONS = 0o777
    FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o777
    FILE_UPLOAD_HANDLERS = [
        'django.core.files.uploadhandler.TemporaryFileUploadHandler',
    ]
    DIRECTORY = ''

    # https://github.com/jazzband/django-configurations/issues/323
    _DEFAULT_AUTO_FIELD = DEFAULT_AUTO_FIELD

    @classmethod
    def setup(cls):
        super().setup()
        # https://github.com/jazzband/django-configurations/issues/323
        cls.DEFAULT_AUTO_FIELD = cls._DEFAULT_AUTO_FIELD
        if cls.FIX_RELATIVE_URLS:
            cls._fix_relative_urls()

    @classmethod
    def post_setup(cls):
        super().post_setup()
        logging.basicConfig(level=logging.INFO, format='*** %(message)s')
        cls.log.info(f'Starting {cls.PROJECT_NAME} project using {cls.__name__} configuration')

    @classmethod
    def _fix_relative_urls(cls):
        for url_attr in ['STATIC_URL', 'MEDIA_URL']:
            url: str = getattr(cls, url_attr)
            if url.startswith('/'):
                url = urljoin(cls.PROJECT_BASE_URL, url)
            if not url.endswith('/'):
                url = f'{url}/'
            setattr(cls, url_attr, url)
