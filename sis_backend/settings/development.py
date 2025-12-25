"""
Development-specific Django settings.
"""
from .base import *
from decouple import config

DEBUG = True

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Alternatively, use PostgreSQL in development
# DATABASES = {
#     'default': {
#         'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.postgresql'),
#         'NAME': config('DATABASE_NAME', default='sis_db'),
#         'USER': config('DATABASE_USER', default='postgres'),
#         'PASSWORD': config('DATABASE_PASSWORD', default=''),
#         'HOST': config('DATABASE_HOST', default='localhost'),
#         'PORT': config('DATABASE_PORT', default='5432'),
#     }
# }

# Email - Console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS - Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Disable SSL in development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Static files - Serve directly in development
STATICFILES_DIRS = []  # Clear base setting
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Logging - More verbose in development
LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'