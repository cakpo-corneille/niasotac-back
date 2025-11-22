#!/usr/bin/env python
"""
Script de gestion de la documentation API
==========================================

Ce script permet de gérer facilement la configuration de la documentation API
sans modifier directement les fichiers .env ou Python.

Usage:
    python manage_api_docs.py status          # Afficher la config actuelle
    python manage_api_docs.py enable          # Activer la documentation
    python manage_api_docs.py disable         # Désactiver la documentation
    python manage_api_docs.py switch yasg     # Basculer vers drf-yasg
    python manage_api_docs.py switch spectacular  # Basculer vers drf-spectacular
    python manage_api_docs.py check           # Vérifier les dépendances
    python manage_api_docs.py urls            # Afficher les URLs disponibles
"""

import os
import sys
import django


def setup_django():
    """Configure Django pour accéder aux settings"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'niasotac_backend.config.dev')
    django.setup()


def print_status():
    """Affiche le statut actuel de la configuration"""
    from niasotac_backend.config.api_docs import (
        is_enabled, get_backend_name, print_config
    )

    print_config()


def enable_docs():
    """Active la documentation API"""
    update_env_file('ENABLE_API_DOCS', 'True')
    print("Documentation API activée")
    print("Redémarrez le serveur Django pour appliquer les changements")


def disable_docs():
    """Désactive la documentation API"""
    update_env_file('ENABLE_API_DOCS', 'False')
    print("Documentation API désactivée")
    print("Redémarrez le serveur Django pour appliquer les changements")


def switch_backend(backend):
    """Change le backend de documentation"""
    if backend not in ['yasg', 'spectacular']:
        print(f"Erreur: Backend '{backend}' invalide")
        print("Backends disponibles: yasg, spectacular")
        sys.exit(1)

    update_env_file('API_DOCS_BACKEND', backend)
    print(f"Backend changé vers: {backend}")
    print("Redémarrez le serveur Django pour appliquer les changements")

    # Vérifier si le package est installé
    check_dependencies(backend)


def check_dependencies(backend=None):
    """Vérifie si les dépendances sont installées"""
    from niasotac_backend.config.api_docs import (
        get_backend_name, get_required_packages
    )

    if backend is None:
        backend = get_backend_name()

    if backend is None:
        print("Documentation API désactivée, aucune vérification nécessaire")
        return

    packages = get_required_packages()[backend]

    print(f"\nVérification des dépendances pour '{backend}':")
    print("-" * 60)

    all_installed = True
    for package in packages:
        package_name = package.split('>=')[0]
        try:
            __import__(package_name.replace('-', '_'))
            print(f"✓ {package_name} installé")
        except ImportError:
            print(f"✗ {package_name} NON installé")
            all_installed = False

    print("-" * 60)

    if not all_installed:
        print("\nPour installer les dépendances manquantes:")
        print(f"  pip install {' '.join(packages)}")
    else:
        print("\nToutes les dépendances sont installées")


def show_urls():
    """Affiche les URLs disponibles"""
    from niasotac_backend.config.api_docs import get_api_docs_urls, is_enabled

    if not is_enabled():
        print("Documentation API désactivée")
        print("Utilisez: python manage_api_docs.py enable")
        return

    urls = get_api_docs_urls()

    if not urls:
        print("Aucune URL disponible (vérifiez les dépendances)")
        print("Utilisez: python manage_api_docs.py check")
        return

    print("\nURLs disponibles:")
    print("-" * 60)
    for url_pattern in urls:
        path = str(url_pattern.pattern)
        name = url_pattern.name if hasattr(url_pattern, 'name') else 'N/A'
        print(f"  /{path:30} (name: {name})")
    print("-" * 60)
    print(f"\nTotal: {len(urls)} endpoints")


def update_env_file(key, value):
    """Met à jour une variable dans le fichier .env"""
    env_file = '.env'

    # Lire le fichier actuel ou créer s'il n'existe pas
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()
    else:
        lines = []

    # Chercher et remplacer ou ajouter la variable
    found = False
    new_lines = []

    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}\n")

    # Écrire le fichier
    with open(env_file, 'w') as f:
        f.writelines(new_lines)


def show_help():
    """Affiche l'aide"""
    print(__doc__)


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    # Commandes qui ne nécessitent pas Django
    if command in ['help', '--help', '-h']:
        show_help()
        return

    # Commandes de configuration
    if command == 'enable':
        enable_docs()
        return

    if command == 'disable':
        disable_docs()
        return

    if command == 'switch':
        if len(sys.argv) < 3:
            print("Erreur: Spécifiez le backend (yasg ou spectacular)")
            sys.exit(1)
        switch_backend(sys.argv[2])
        return

    # Commandes nécessitant Django
    setup_django()

    if command == 'status':
        print_status()
    elif command == 'check':
        check_dependencies()
    elif command == 'urls':
        show_urls()
    else:
        print(f"Commande inconnue: {command}")
        show_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
