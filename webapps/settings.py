"""
Django settings for webapps project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import ConfigParser
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hsz$%9_4jak+skd%7cr)cfku+n!1t0hn#fn_e=y+!69flp@1x0'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'socialnetwork'
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# Used by the authentication system for the private-todo-list application.
# URL to use if the authentication system requires a user to log in.
LOGIN_URL = '/socialnetwork/login'

# Default URL to redirect to after a user logs in.
LOGIN_REDIRECT_URL = '/socialnetwork/'

ROOT_URLCONF = 'webapps.urls'

WSGI_APPLICATION = 'webapps.wsgi.application'

# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#             'NAME': 'hw7',                      # Or path to database file if using sqlite3.
#             # The following settings are not used with sqlite3:
#             'USER': 'hw7',
#             'PASSWORD': 'hw7',
#             'HOST': 'localhost',                      # Empty for localhost through domain sockets or           '127.0.0.1' for localhost through TCP.
#             'PORT': '',                      # Set to empty string for default.
#         }
#     }

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases


import dj_database_url
DATABASES={}
DATABASES['default'] =  dj_database_url.config()
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

FILE_UPLOAD_MAX_MEMORY_SIZE = 2500000

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
config = ConfigParser.ConfigParser()
config.read("config.ini")

EMAIL_HOST = os.environ.get('Host')
EMAIL_PORT = os.environ.get('Port')
EMAIL_HOST_USER = os.environ.get('User')
EMAIL_HOST_PASSWORD = os.environ.get('Password')
EMAIL_USE_SSL = True
