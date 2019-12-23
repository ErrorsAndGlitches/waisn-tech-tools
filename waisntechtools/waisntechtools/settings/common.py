"""
Django settings for waisntechtools project.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/

Quick-start development settings - unsuitable for production
See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

Database
https://docs.djangoproject.com/en/2.1/ref/settings/#databases
"""

import os
from os import environ

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))

# Application definition

INSTALLED_APPS = [
    'alerts.apps.AlertsConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'social_django',
    'twilio',
    'django_twilio',
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

ROOT_URLCONF = 'waisntechtools.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'waisntechtools.wsgi.application'

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
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'

# BEGIN Auth0
WAISN_AUTH_DISABLED = environ.get('WAISN_AUTH_DISABLED', False)


def environ_var(key):
    """Used to allow tests to run without having to set the environment variables. If this gets unwieldy, we should
    think about having a separate test settings file. If testing mode, returns the key name as the value."""
    import sys
    if 'test' in sys.argv:
        return key
    else:
        return environ[key]


SOCIAL_AUTH_TRAILING_SLASH = False  # Remove trailing slash from routes
SOCIAL_AUTH_AUTH0_DOMAIN = environ_var('AUTH0_DOMAIN')
SOCIAL_AUTH_AUTH0_KEY = environ_var('AUTH0_KEY')
SOCIAL_AUTH_AUTH0_SECRET = environ_var('AUTH0_SECRET')
SOCIAL_AUTH_AUTH0_SCOPE = [
    'openid',
    'profile'
]

TWILIO_ACCOUNT_SID = environ_var('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = environ_var('TWILIO_AUTH_TOKEN')
TWILIO_SMS_NUMBER = environ_var('TWILIO_SMS_NUMBER')

AUTHENTICATION_BACKENDS = {
    'alerts.auth0backend.Auth0',
    'django.contrib.auth.backends.ModelBackend'
}

LOGIN_URL = '/login/auth0'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
# END Auth0
