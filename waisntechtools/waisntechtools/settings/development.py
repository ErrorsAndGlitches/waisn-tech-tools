import os
from os import environ

from waisntechtools.settings.common import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n2+o$1^tiwv)s2jx@rsn1-rkv(r@0x1-e&jsp2r-@v8pye8ydt'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['.ngrok.io', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
