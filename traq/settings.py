import os
from fnmatch import fnmatch
from django.conf import global_settings
from varlet import variable
import pymysql
pymysql.install_as_MySQLdb()


PROJECT_DIR = os.path.dirname(__file__)
HOME_DIR = os.path.normpath(os.path.join(PROJECT_DIR, '../'))

DEBUG = variable("DEBUG", default=False)
TEMPLATE_DEBUG = DEBUG

# if you're having trouble connecting to LDAP set this to True so you can login
# to track, bypassing LDAP group checks
LDAP_DISABLED = variable("LDAP_DISABLED", default=False)

LDAP = {
    'default': {
        'host': "ldap://ldap-login.oit.pdx.edu",
        'username': 'traq',
        'password': '',
        'search_dn': 'dc=pdx,dc=edu'
    }
}

# ('Your Name', 'your_email@example.com'),
ADMINS = variable("ADMINS", [])
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': variable("DB_NAME", 'traq'),
        'USER': variable("DB_USER", 'root'),
        'PASSWORD': variable("DB_PASSWORD", ''),
        'HOST': '',
        'PORT': '',
    }
}

BASE_URL = 'http://traq.research.pdx.edu' # no trailing slash

# When an email is sent to a user, the address is formed by username@EMAIL_DOMAIN
EMAIL_DOMAIN = 'pdx.edu'

# we need to use the pickler since we save abitrary objects to sessions
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

# allow the use of wildcards in the INTERAL_IPS setting
class IPList(list):
    # do a unix-like glob match
    # E.g. '192.168.1.100' would match '192.*'
    def __contains__(self, ip):
        for ip_pattern in self:
            if fnmatch(ip, ip_pattern):
                return True
        return False

INTERNAL_IPS = IPList(['10.*', '192.168.*'])

CAS_SERVER_URL = 'https://sso.pdx.edu/cas/login'
# prevents CAS login on the admin pages
CAS_ADMIN_PREFIX = 'admin'

# for django-cas to work, it needs HttpRequest.get_host(), which requires this setting
# https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.pdx.edu']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'US/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(HOME_DIR, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(HOME_DIR, "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, "static"),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

ATOMIC_REQUESTS = True

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'djangocas.middleware.CASMiddleware',
    'cloak.middleware.CloakMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'traq.backends.PSUBackend',
)

ROOT_URLCONF = 'traq.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'traq.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_DIR, 'templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = global_settings.TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.request',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'arcutils',
    'traq.projects',
    'traq.todos',
    'traq.tickets',
    'traq.accounts',
    'traq',
    'model_mommy',
    'cloak',
    'coverage',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django_extensions',
)

SECRET_KEY = variable("SECRET_KEY", default=os.urandom(64).decode("latin1"))
