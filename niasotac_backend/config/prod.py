"""
Production settings - SÉCURISÉ pour déploiement
Toutes les valeurs sensibles DOIVENT venir des variables d'environnement
"""
from .base import *
from decouple import config
import dj_database_url
import os

# =============================================================================
# SÉCURITÉ CRITIQUE
# =============================================================================

# DEBUG doit TOUJOURS être False en production (pas de fallback)
DEBUG = False

# Secret key OBLIGATOIRE depuis l'environnement (pas de fallback)
SECRET_KEY = os.environ['SECRET_KEY']  # Crash si absent - VOULU

# ALLOWED_HOSTS obligatoire - pas de wildcard
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split(',')

# =============================================================================
# HEADERS DE SÉCURITÉ
# =============================================================================

# Force HTTPS redirect
SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = config('SECURE_HSTS_SECONDS', default=31536000, cast=int)  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Protection XSS
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Protection Clickjacking
X_FRAME_OPTIONS = 'DENY'

# Proxy headers (si derrière un reverse proxy)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# CORS - WHITELIST UNIQUEMENT
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='',
    cast=lambda v: [origin.strip() for origin in v.split(',') if origin.strip()]
)

CORS_ALLOW_CREDENTIALS = True

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [origin.strip() for origin in v.split(',') if origin.strip()]
)

# =============================================================================
# BASE DE DONNÉES
# =============================================================================

# PostgreSQL via DATABASE_URL (OBLIGATOIRE en production)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=config('DB_SSL_REQUIRE', default=True, cast=bool)
        )
    }
else:
    # Fallback SQLite UNIQUEMENT pour tests (à désactiver en prod réelle)
    import warnings
    warnings.warn("DATABASE_URL non défini - utilisation de SQLite (NON RECOMMANDÉ EN PRODUCTION)")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# STOCKAGE FICHIERS - AWS S3
# =============================================================================

# Stockage des médias sur S3 (images produits, uploads)
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-west-3')
    
    # S3 Security
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 jour
    }
    
    # Storage backends
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # URLs
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
else:
    # Fallback stockage local (non recommandé en production)
    import warnings
    warnings.warn("USE_S3=False - Stockage local utilisé (fichiers perdus au redéploiement)")

# Fichiers statiques toujours avec Whitenoise (pas S3)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# =============================================================================
# CELERY - REDIS
# =============================================================================

# Redis OBLIGATOIRE en production
CELERY_BROKER_URL = os.environ.get('REDIS_URL', os.environ.get('CELERY_BROKER_URL'))
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', os.environ.get('CELERY_RESULT_BACKEND'))

if not CELERY_BROKER_URL:
    import warnings
    warnings.warn("REDIS_URL non défini - Celery ne fonctionnera pas correctement")

# =============================================================================
# EMAIL
# =============================================================================

# Configuration email pour newsletters
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# =============================================================================
# LOGGING
# =============================================================================

# Créer le dossier logs AVANT la configuration (sinon RotatingFileHandler crash)
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s'
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'production.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'json' if config('LOG_JSON', default=False, cast=bool) else 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': config('LOG_LEVEL', default='INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': config('CELERY_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# =============================================================================
# MONITORING - SENTRY (optionnel mais recommandé)
# =============================================================================

SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        environment=config('SENTRY_ENVIRONMENT', default='production'),
        traces_sample_rate=config('SENTRY_TRACES_SAMPLE_RATE', default=0.1, cast=float),
        send_default_pii=False,
    )

# =============================================================================
# PERFORMANCE
# =============================================================================

# Cache avec Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Session backend sur Redis (optionnel, plus performant)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# =============================================================================
# LIMITES ET QUOTAS
# =============================================================================

# Limites upload
FILE_UPLOAD_MAX_MEMORY_SIZE = config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int)  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int)  # 5MB

# Limites requêtes
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# =============================================================================
# JWT PRODUCTION
# =============================================================================

SIMPLE_JWT = {
    **SIMPLE_JWT,  # Hérite de base.py
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),  # Plus court en production
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # Activé en production
}
