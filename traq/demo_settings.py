from .settings import LDAP_URL, LDAP_BASE_DN

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_URL = 'http://traq.research.pdx.edu' # no trailing slash

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

LDAP = {
    'default': {
        'host': LDAP_URL,
        'username': 'traq',
        'password': '',
        'search_dn': LDAP_BASE_DN,
    }
}

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''
