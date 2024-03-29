# Django settings for winedora project.

import os
import djcelery
djcelery.setup_loader()

BROKER_URL = os.environ.get('CLOUDAMQP_URL', 'amqp://guest:guest@localhost:5672//')

USE_CELERY = True

# need to get directory of parent-parent since settings.py in two layers below
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir))

if 'DEBUG' in os.environ and os.environ['DEBUG'] == 'true':
  DEBUG = True
else:
  DEBUG = False

if 'NEW_PARTY' in os.environ and os.environ['NEW_PARTY'] == 'true':
  NEW_PARTY = True
else:
  NEW_PARTY = False

try:
  from winedora.settings_debug import *
except Exception as e:
  print e

TEMPLATE_DEBUG = DEBUG

if 'DEPLOY' in os.environ and os.environ['DEPLOY'] == 'true':
  DEPLOY = True  # only True if production (for mail settings and https)
else:
  DEPLOY = False

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('Billy Odero', 'billy@vinely.com'),
    ('Kwan Lee', 'kwan@vinely.com'),
)

# defaults to /accounts/profile/
#LOGIN_REDIRECT_URL =

import django.conf.global_settings as DEFAULT_SETTINGS

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_SETTINGS.TEMPLATE_CONTEXT_PROCESSORS + (
    "main.context_processors.vinely_user_info",
    "django.core.context_processors.request",
)


MANAGERS = ADMINS

import dj_database_url
DATABASES = {'default': dj_database_url.config(default='postgres://localhost')}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
"""

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.htm
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

AWS_ACCESS_KEY_ID = 'AKIAIA5QIVHATQ54TYBQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'cdn.vinely.com'
if NEW_PARTY:
  AWS_STORAGE_BUCKET_NAME = 'cdn.newparty.vinely.com'
  from boto.s3.connection import OrdinaryCallingFormat
  AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
AWS_PRELOAD_METADATA = True

if DEPLOY:
  # for handling https static file serving
  from boto.s3.connection import OrdinaryCallingFormat
  AWS_S3_CALLING_FORMAT = OrdinaryCallingFormat()
else:
  # for static files to serve from http
  AWS_S3_SECURE_URLS = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = PROJECT_ROOT + '/sitemedia/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'http://s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = PROJECT_ROOT + '/sitestatic/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = 'http://s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
#STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT + '/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
    'compressor.finders.CompressorFinder',
)

# AWS_S3_CUSTOM_DOMAIN = 'our own cname for the s3 bucket'
EMAIL_STATIC_URL = 'http://s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME

if DEBUG is False:
  # if production

  #DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
  #STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
  #DEFAULT_FILE_STORAGE = 'winedora.s3utils.MediaRootS3BotoStorage'
  #STATICFILES_STORAGE = 'winedora.s3utils.StaticRootS3BotoStorage'
  DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
  DEFAULT_S3_PATH = 'media'
  STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
  STATIC_S3_PATH = 'static'

  MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
  MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME
  STATIC_ROOT = '/%s/' % STATIC_S3_PATH
  STATIC_URL = '//s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
  ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'
else:
  DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
  DEFAULT_S3_PATH = 'media'
  if NEW_PARTY:
    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

# Make this unique, and don't share it with anybody.
SECRET_KEY = '=a_x8@e-h+ia(^*4y_xkm5=g*z&amp;w$bu&amp;rt@$j*urok)fj0rw7('

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

if DEPLOY:
  # enable SSL
  MIDDLEWARE_CLASSES = (
      'sslify.middleware.SSLifyMiddleware',
      'django.middleware.gzip.GZipMiddleware',
      'johnny.middleware.LocalStoreClearMiddleware',
      'johnny.middleware.QueryCacheMiddleware',
      'django.middleware.common.CommonMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.transaction.TransactionMiddleware',
      'winedora.middleware.ImpersonateMiddleware',
      'api.middleware.XsSharing',
      # Uncomment the next line for simple clickjacking protection:
      # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
  )
else:
  MIDDLEWARE_CLASSES = (
      'django.middleware.gzip.GZipMiddleware',
      'johnny.middleware.LocalStoreClearMiddleware',
      'johnny.middleware.QueryCacheMiddleware',
      'django.middleware.common.CommonMiddleware',
      'django.contrib.sessions.middleware.SessionMiddleware',
      'django.middleware.csrf.CsrfViewMiddleware',
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'django.contrib.messages.middleware.MessageMiddleware',
      'django.middleware.transaction.TransactionMiddleware',
      'winedora.middleware.ImpersonateMiddleware',
      'api.middleware.XsSharing',
      'api_logger.middleware.APILogMiddleWare',
      # Uncomment the next line for simple clickjacking protection:
      # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
  )

ROOT_URLCONF = 'winedora.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'winedora.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    PROJECT_ROOT + '/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'fluent_dashboard',
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'personality',
    'accounts',
    'sorl.thumbnail',
    'main',
    'winedora',
    'south',
    'emailusernames',
    'gunicorn',
    's3_folder_storage',
    'compressor',
    'support',
    'social',
    'cms',
    'stripecard',
    'django_tables2',
    'tinymce',
    'pro',
    'djcelery',
    'coupon',
    'api',
    'api_logger',
    'tastypie',
    'tastypie_swagger',
)

TASTYPIE_SWAGGER_API_MODULE = 'api.tools.api'

SOUTH_TESTS_MIGRATE = False

AUTH_PROFILE_MODULE = 'accounts.UserProfile'

AUTHENTICATION_BACKENDS = (
    'emailusernames.backends.EmailAuthBackend',
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

if DEPLOY:
  # SENDGRID
  #EMAIL_HOST = 'smtp.sendgrid.net'
  #EMAIL_PORT = '587'
  #EMAIL_HOST_USER = os.environ.get('SENDGRID_USERNAME')
  #EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_PASSWORD')
  #EMAIL_USE_TLS = True
  # MAILGUN
  EMAIL_HOST = os.environ.get('MAILGUN_SMTP_SERVER')
  EMAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT')  # 587
  EMAIL_HOST_USER = os.environ.get('MAILGUN_SMTP_LOGIN')
  EMAIL_HOST_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')
else:
  # EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
  # EMAIL_FILE_PATH = PROJECT_ROOT + '/emails/'
  EMAIL_BACKEND = 'main.backends.EmailSinkBackend'
  EMAIL_HOST = 'smtp.gmail.com'
  EMAIL_PORT = 587
  EMAIL_HOST_USER = 'tech@vinely.com'
  EMAIL_HOST_PASSWORD = 'hi2winedora'
  EMAIL_USE_TLS = True
  EMAIL_TEST_ACCOUNT = 'vinelytesting@gmail.com'

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# https://devcenter.heroku.com/articles/django-memcache
try:
  cache_servers = os.environ['MEMCACHIER_SERVERS']
  os.environ['MEMCACHE_SERVERS'] = cache_servers.replace(',', ';')
  os.environ['MEMCACHE_USERNAME'] = os.environ.get('MEMCACHIER_USERNAME', '')
  os.environ['MEMCACHE_PASSWORD'] = os.environ.get('MEMCACHIER_PASSWORD', '')

  CACHES = {
      'default': {
          # 'BACKEND': 'winedora.backends.memcached.PyLibMCCache',
          'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
          'LOCATION': os.environ.get('MEMCACHIER_SERVERS', '').replace(',', ';'),
          'TIMEOUT': 500,
          'BINARY': True,
          'JOHNNY_CACHE': True,
          'OPTIONS': {  # Maps to pylibmc "behaviors"
              'tcp_nodelay': True,
              'ketama': True
          }
      }
  }

  JOHNNY_TABLE_BLACKLIST = (
      'support_email', 'main_personalog',
      'main_prosignuplog', 'main_thankyounote',
      'main_engagementinterest'
  )
except:
  CACHES = {
      'default': {
          'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
      }
  }

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'normal': {
            'format': '[%(asctime)s]:[%(levelname)s][%(name)s:%(lineno)d] %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'normal'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'personality': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'accounts': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'support': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'main': {
            'handlers': ['console'],
            'level': 'INFO'
        },
        'coupon': {
            'handlers': ['console'],
            'level': 'INFO'
        },
    },
}

try:
  from winedora.settings_local import *
except Exception as e:
  print e


if DEPLOY:
  # STRIPE_SECRET = "sk_0B7BUorM8xQM2qwao7dZCqxtPzjDA"
  # STRIPE_PUBLISHABLE = "pk_0B7BkfhSTrZvTa6F4fCis0RCNPnbd"
  STRIPE_SECRET_CA = "sk_live_60XINxPEMjcCqCewtAif2q29"
  STRIPE_PUBLISHABLE_CA = "pk_live_5lRoqyXhbwPFHjlvbT7k9C16"
else:
  # STRIPE_SECRET = "sk_0B7BJP63oAFG6ZwL0TcbWPUWU0LuM"
  # STRIPE_PUBLISHABLE = "pk_0B7BHz0y806TkUPZgpOBepr4dVngO"
  STRIPE_SECRET_CA = "sk_test_eNRrnFXyqS6pQmNuKnI8HWIO"
  STRIPE_PUBLISHABLE_CA = "pk_test_KXVrxVwsOQ6359kaGhrwUyrG"

# TINYMCE_DEFAULT_CONFIG = {
#   'content_css': STATIC_URL + 'fonts/AlternateGothicKit/MyFontsWebfontsOrderM3947119.css',
#   'theme_advanced_fonts': STATIC_URL + 'fonts/AlternateGothicKit/MyFontsWebfontsOrderM3947119.css',
#   'theme': 'simple',
#   'font_size_style_values': 'medium',
#   'theme_advanced_font_sizes': 'medium',
# }

ADMIN_TOOLS_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentIndexDashboard'
ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'fluent_dashboard.dashboard.FluentAppIndexDashboard'
ADMIN_TOOLS_MENU = 'fluent_dashboard.menu.FluentMenu'

FLUENT_DASHBOARD_CMS_PAGE_MODEL = ('cms', 'contenttemplate')

FLUENT_DASHBOARD_APP_ICONS = {
    'accounts/userprofile': 'preferences-contact-list.png',
    'accounts/address': 'go-home.png',
    'accounts/subscriptioninfo': 'view-time-schedule.png',
    'personality/wineratingdata': 'mail-mark-task.png',
    'main/party': 'view-resource-calendar.png',
    'main/unconfirmedparty': 'x-office-calendar.png',
    'main/customizeorder': 'basket.png',
    'main/newhostnoparty': 'meeting-participant.png',
    'main/order': 'utilities-file-archiver.png',
    'main/prosignuplog': 'view-calendar-journal.png',
    'main/engagementinterest': 'x-office-contact.png',
    'main/partyinvite': 'list-add-user.png',
    'pro/monthlybonuscompensation': 'view-bank-account.png',
    'pro/weeklycompensation': 'help-donate.png',
    'pro/monthlyqualification': 'office-chart-area.png',
    'support/wineinventory': 'view-choose.png',
#     'company/company': 'office-chart-pie.png',
#     'main/location': 'go-home.png',
#     'main/service': 'preferences-system-network.png',
#     'main/education': 'document-edit.png',
#     'main/skill': 'applications-engineering.png',
}

FLUENT_DASHBOARD_APP_GROUPS = (
    ('Applications', {
        'models': ('*',),
        'module': 'AppList',
        'collapsible': True,
    }),
    ('Administration', {
        'models': (
            'django.contrib.auth.*',
            'django.contrib.sites.*',
            'accounts.*',
        ),
    }),
    ('Main', {
        'models': ('main.*',),
    }),
    ('Personality', {
        'models': ('personality.*',),
    }),
    ('Pro', {
        'models': ('pro.*',),
    }),
    ('Support', {
        'models': ('support.*',),
    }),
    ('Maintenance', {
        'models': ('djcelery.*', 'tastypie.*',),
    }),

)