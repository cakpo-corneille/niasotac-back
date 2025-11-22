"""
Configuration modulaire de la documentation API
================================================

Ce module centralise toute la configuration de la documentation API (Swagger/ReDoc).
Il permet d'activer/désactiver facilement la documentation et de choisir entre
différents outils de documentation.

Configuration via variables d'environnement:
- ENABLE_API_DOCS: True/False (défaut: True en dev, False en prod)
- API_DOCS_BACKEND: 'yasg' ou 'spectacular' (défaut: 'yasg')
- API_DOCS_REQUIRE_AUTH: True/False (défaut: False)

Usage dans urls.py:
    from niasotac_backend.config.api_docs import get_api_docs_urls

    urlpatterns = [
        ...
    ] + get_api_docs_urls()
"""

from decouple import config
from django.conf import settings


# ============================================================================
# CONFIGURATION GLOBALE
# ============================================================================

ENABLE_API_DOCS = config(
    'ENABLE_API_DOCS',
    default=settings.DEBUG,  # Activé par défaut en dev
    cast=bool
)

API_DOCS_BACKEND = config(
    'API_DOCS_BACKEND',
    default='yasg',  # Options: 'yasg' ou 'spectacular'
    cast=str
)

API_DOCS_REQUIRE_AUTH = config(
    'API_DOCS_REQUIRE_AUTH',
    default=False,
    cast=bool
)


# ============================================================================
# CONFIGURATION DRF-YASG
# ============================================================================

YASG_INFO = {
    'title': "NIASOTAC API",
    'default_version': 'v1',
    'description': """
    Documentation complète de l'API vitrine NIASOTAC

    ## Authentification
    Cette API utilise JWT (JSON Web Tokens) pour l'authentification.

    Pour obtenir un token:
    1. POST /api/token/ avec {username, password}
    2. Utilisez le token dans le header: Authorization: Bearer {token}

    ## Endpoints disponibles
    - Products: Gestion des produits
    - Categories: Gestion des catégories (arborescence MPTT)
    - Promotions: Gestion des promotions et réductions
    - Newsletter: Gestion des abonnements newsletter
    - Settings: Paramètres du site
    """,
    'terms_of_service': "https://www.niasotac.com/terms/",
    'contact': {
        'email': "contact@niasotac.com",
        'name': "Support NIASOTAC",
    },
    'license': {
        'name': "MIT License",
        'url': "https://opensource.org/licenses/MIT"
    },
}

YASG_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'JWT Authorization header. Format: "Bearer {token}"'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'SHOW_REQUEST_HEADERS': True,
    'SUPPORTED_SUBMIT_METHODS': [
        'get', 'post', 'put', 'patch', 'delete'
    ],
    'OPERATIONS_SORTER': 'alpha',
    'TAGS_SORTER': 'alpha',
    'DOC_EXPANSION': 'none',
    'DEEP_LINKING': True,
    'DISPLAY_OPERATION_ID': False,
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_MODEL_DEPTH': 3,
}


# ============================================================================
# CONFIGURATION DRF-SPECTACULAR
# ============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'NIASOTAC API',
    'DESCRIPTION': 'API REST pour la gestion de produits, catégories, promotions et newsletters',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/v[0-9]',
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,

    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'defaultModelsExpandDepth': 1,
        'defaultModelExpandDepth': 1,
        'displayRequestDuration': True,
        'docExpansion': 'none',
        'filter': True,
        'operationsSorter': 'alpha',
        'showExtensions': True,
        'showCommonExtensions': True,
        'tagsSorter': 'alpha',
    },

    'REDOC_UI_SETTINGS': {
        'hideDownloadButton': False,
        'expandResponses': '200,201',
        'pathInMiddlePanel': True,
        'nativeScrollbars': True,
        'theme': {
            'colors': {
                'primary': {
                    'main': '#2196F3'
                }
            },
            'typography': {
                'fontSize': '14px',
                'fontFamily': '"Roboto", sans-serif',
                'headings': {
                    'fontFamily': '"Roboto", sans-serif'
                }
            }
        }
    },

    'PREPROCESSING_HOOKS': [],
    'POSTPROCESSING_HOOKS': [],
    'ENUM_NAME_OVERRIDES': {},
    'SERVE_PERMISSIONS': ['rest_framework.permissions.AllowAny'],
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


# ============================================================================
# FONCTIONS PUBLIQUES
# ============================================================================

def get_api_docs_urls():
    """
    Retourne les URLs de documentation API selon la configuration.

    Returns:
        list: Liste des patterns d'URL ou liste vide si désactivé

    Example:
        # Dans urls.py
        urlpatterns = [
            path('admin/', admin.site.urls),
            path('api/v1/', include('showcase.urls')),
        ] + get_api_docs_urls()
    """
    if not ENABLE_API_DOCS:
        return []

    if API_DOCS_BACKEND == 'spectacular':
        return _get_spectacular_urls()
    else:
        return _get_yasg_urls()


def get_installed_apps():
    """
    Retourne les apps Django nécessaires pour la documentation.

    Returns:
        list: Liste des apps à ajouter dans INSTALLED_APPS

    Example:
        # Dans settings.py
        INSTALLED_APPS = [
            ...
        ] + get_installed_apps()
    """
    if not ENABLE_API_DOCS:
        return []

    if API_DOCS_BACKEND == 'spectacular':
        return ['drf_spectacular']
    else:
        return ['drf_yasg']


def get_required_packages():
    """
    Retourne les packages Python nécessaires.
    Utile pour générer requirements.txt ou vérifier les dépendances.

    Returns:
        dict: Dictionnaire {backend: [packages]}
    """
    return {
        'yasg': ['drf-yasg>=1.21.7'],
        'spectacular': ['drf-spectacular>=0.27.0'],
    }


# ============================================================================
# FONCTIONS INTERNES
# ============================================================================

def _get_yasg_urls():
    """Génère les URLs pour drf-yasg"""
    try:
        from django.urls import path
        from rest_framework import permissions
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi

        # Déterminer les permissions
        permission_classes = [permissions.AllowAny]
        if API_DOCS_REQUIRE_AUTH:
            permission_classes = [permissions.IsAuthenticated]

        # Créer le schema view
        schema_view = get_schema_view(
            openapi.Info(
                title=YASG_INFO['title'],
                default_version=YASG_INFO['default_version'],
                description=YASG_INFO['description'],
                terms_of_service=YASG_INFO['terms_of_service'],
                contact=openapi.Contact(**YASG_INFO['contact']),
                license=openapi.License(**YASG_INFO['license']),
            ),
            public=True,
            permission_classes=permission_classes,
        )

        return [
            path(
                'swagger.json',
                schema_view.without_ui(cache_timeout=0),
                name='schema-json'
            ),
            path(
                'swagger.yaml',
                schema_view.without_ui(cache_timeout=0),
                name='schema-yaml'
            ),
            path(
                'swagger/',
                schema_view.with_ui('swagger', cache_timeout=0),
                name='schema-swagger-ui'
            ),
            path(
                'redoc/',
                schema_view.with_ui('redoc', cache_timeout=0),
                name='schema-redoc'
            ),
        ]
    except ImportError:
        print("WARNING: drf-yasg n'est pas installé. Installez-le avec: pip install drf-yasg")
        return []


def _get_spectacular_urls():
    """Génère les URLs pour drf-spectacular"""
    try:
        from django.urls import path
        from drf_spectacular.views import (
            SpectacularAPIView,
            SpectacularRedocView,
            SpectacularSwaggerView
        )

        return [
            path(
                'swagger/schema/',
                SpectacularAPIView.as_view(),
                name='schema'
            ),
            path(
                'swagger/',
                SpectacularSwaggerView.as_view(url_name='schema'),
                name='swagger-ui'
            ),
            path(
                'redoc/',
                SpectacularRedocView.as_view(url_name='schema'),
                name='redoc'
            ),
        ]
    except ImportError:
        print("WARNING: drf-spectacular n'est pas installé. Installez-le avec: pip install drf-spectacular")
        return []


def is_enabled():
    """Vérifie si la documentation API est activée"""
    return ENABLE_API_DOCS


def get_backend_name():
    """Retourne le nom du backend utilisé"""
    return API_DOCS_BACKEND if ENABLE_API_DOCS else None


# ============================================================================
# UTILITAIRES DE DIAGNOSTIC
# ============================================================================

def print_config():
    """Affiche la configuration actuelle (utile pour debugging)"""
    print("=" * 60)
    print("CONFIGURATION DOCUMENTATION API")
    print("=" * 60)
    print(f"Activée: {ENABLE_API_DOCS}")
    print(f"Backend: {API_DOCS_BACKEND if ENABLE_API_DOCS else 'N/A'}")
    print(f"Authentification requise: {API_DOCS_REQUIRE_AUTH}")
    print(f"URLs disponibles: {len(get_api_docs_urls())} endpoints")
    print("=" * 60)

    if ENABLE_API_DOCS:
        urls = get_api_docs_urls()
        if urls:
            print("\nEndpoints disponibles:")
            for url_pattern in urls:
                print(f"  - /{url_pattern.pattern}")
    else:
        print("\nDocumentation API désactivée")
    print()
