"""
Django settings module initialization.
Automatically imports the correct settings based on environment.
"""
from decouple import config

# Determine which settings to use
ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *