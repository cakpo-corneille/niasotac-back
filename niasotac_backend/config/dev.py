"""
Development settings - Permissif pour faciliter le développement
"""
from .base import *
import os

# =============================================================================
# DÉVELOPPEMENT - PERMISSIF
# =============================================================================

DEBUG = True

# Accepte toutes les origines en développement
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '*']

# Secret key pour dev (pas de sécurité critique en local)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-dev-key-not-for-production')

# =============================================================================
# CORS - PERMISSIF EN DEV
# =============================================================================

# Accepte toutes les origines en développement (React, Vue, etc. en local)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins for Replit
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:5000', 'http://127.0.0.1:3000', 'http://127.0.0.1:5000']

# Ajouter les domaines Replit si présents
replit_domains = os.getenv('REPLIT_DOMAINS', '')
if replit_domains:
    for domain in replit_domains.split(','):
        domain = domain.strip()
        if domain:
            CSRF_TRUSTED_ORIGINS.append(f'https://{domain}')
            CSRF_TRUSTED_ORIGINS.append(f'http://{domain}')

# =============================================================================
# EMAIL - CONSOLE EN DEV (pas d'envoi réel)
# =============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# =============================================================================
# LOGGING SIMPLE
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =============================================================================
# FRONTEND
# =============================================================================

FRONTEND_URL = "http://localhost:5000"