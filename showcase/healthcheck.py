"""
Healthcheck endpoint pour monitoring et orchestration
"""
from django.http import JsonResponse
from django.conf import settings
from django.db import connection
from django.core.cache import cache
import sys


def healthcheck(request):
    """
    Endpoint de healthcheck pour vérifier la santé de l'application
    GET /health/
    
    Retourne:
    - 200 OK si tout fonctionne
    - 503 Service Unavailable si un service critique est down
    """
    health_status = {
        "status": "healthy",
        "checks": {},
        "version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    all_healthy = True
    
    # Check 1: Database
    try:
        connection.ensure_connection()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        all_healthy = False
    
    # Check 2: Cache (Redis)
    try:
        cache.set('healthcheck', 'ok', 10)
        cached = cache.get('healthcheck')
        if cached == 'ok':
            health_status["checks"]["cache"] = "healthy"
        else:
            health_status["checks"]["cache"] = "unhealthy: cache not working"
            all_healthy = False
    except Exception as e:
        health_status["checks"]["cache"] = f"unhealthy: {str(e)}"
        all_healthy = False
    
    # Check 3: Settings
    health_status["checks"]["debug_mode"] = "ON" if settings.DEBUG else "OFF"
    
    # Status global
    if not all_healthy:
        health_status["status"] = "unhealthy"
        return JsonResponse(health_status, status=503)
    
    return JsonResponse(health_status, status=200)


def readiness(request):
    """
    Endpoint de readiness pour Kubernetes/orchestration
    GET /ready/
    
    Vérifie si l'app est prête à recevoir du trafic
    """
    try:
        # Vérifier si Django est chargé
        from django.apps import apps
        apps.check_apps_ready()
        
        # Vérifier la DB
        connection.ensure_connection()
        
        return JsonResponse({"status": "ready"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "not ready", "error": str(e)}, status=503)


def liveness(request):
    """
    Endpoint de liveness pour Kubernetes/orchestration
    GET /alive/
    
    Vérifie si l'app est vivante (pas bloquée/deadlock)
    """
    return JsonResponse({"status": "alive"}, status=200)
