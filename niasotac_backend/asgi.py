"""
ASGI config for niasotac_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Utilise DJANGO_SETTINGS_MODULE depuis l'environnement
# En production: exporter DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    os.getenv('DJANGO_SETTINGS_MODULE', 'niasotac_backend.config.prod')
)

application = get_asgi_application()
