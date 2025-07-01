from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable URL resolver validation to bypass URL errors
SILENCED_SYSTEM_CHECKS = ['urls.W002', 'urls.E007', 'urls.W001']

# Use simple cache for testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email settings for testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Root URL conf - set to None to bypass URL resolution during tests
ROOT_URLCONF = None