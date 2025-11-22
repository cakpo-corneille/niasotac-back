#!/usr/bin/env python3
"""
Test de validation de la configuration API Docs
"""

import sys
import os

# Tests de base sans Django
def test_file_structure():
    """Vérifie que tous les fichiers sont en place"""
    print("Test 1: Structure des fichiers")
    print("-" * 60)

    required_files = [
        'niasotac_backend/config/api_docs.py',
        'niasotac_backend/config/API_DOCS_CONFIG.md',
        'manage_api_docs.py',
        'MIGRATION_API_DOCS.md',
        '.env.example',
    ]

    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"  {status} {file_path}")
        if not exists:
            all_exist = False

    print("-" * 60)
    return all_exist


def test_imports():
    """Vérifie que les imports de base fonctionnent"""
    print("\nTest 2: Imports de base")
    print("-" * 60)

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from niasotac_backend.config import api_docs
        print("  ✓ Import de api_docs.py réussi")

        # Vérifier les fonctions principales
        required_functions = [
            'get_api_docs_urls',
            'get_installed_apps',
            'get_required_packages',
            'is_enabled',
            'get_backend_name',
            'print_config'
        ]

        for func_name in required_functions:
            if hasattr(api_docs, func_name):
                print(f"  ✓ Fonction '{func_name}' disponible")
            else:
                print(f"  ✗ Fonction '{func_name}' manquante")
                return False

        print("-" * 60)
        return True

    except ImportError as e:
        print(f"  ✗ Erreur d'import: {e}")
        print("-" * 60)
        return False


def test_configuration_values():
    """Vérifie les valeurs de configuration par défaut"""
    print("\nTest 3: Valeurs de configuration")
    print("-" * 60)

    try:
        from niasotac_backend.config import api_docs

        # Test des constantes
        print(f"  ENABLE_API_DOCS: {api_docs.ENABLE_API_DOCS}")
        print(f"  API_DOCS_BACKEND: {api_docs.API_DOCS_BACKEND}")
        print(f"  API_DOCS_REQUIRE_AUTH: {api_docs.API_DOCS_REQUIRE_AUTH}")

        # Vérifier que les backends sont valides
        if api_docs.API_DOCS_BACKEND not in ['yasg', 'spectacular']:
            print(f"  ✗ Backend invalide: {api_docs.API_DOCS_BACKEND}")
            return False

        print("  ✓ Configuration valide")
        print("-" * 60)
        return True

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        print("-" * 60)
        return False


def test_required_packages():
    """Teste la fonction get_required_packages"""
    print("\nTest 4: Packages requis")
    print("-" * 60)

    try:
        from niasotac_backend.config import api_docs

        packages = api_docs.get_required_packages()

        if 'yasg' in packages:
            print(f"  ✓ Packages YASG: {packages['yasg']}")
        else:
            print("  ✗ Packages YASG manquants")
            return False

        if 'spectacular' in packages:
            print(f"  ✓ Packages Spectacular: {packages['spectacular']}")
        else:
            print("  ✗ Packages Spectacular manquants")
            return False

        print("-" * 60)
        return True

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        print("-" * 60)
        return False


def test_env_example():
    """Vérifie que .env.example contient les bonnes variables"""
    print("\nTest 5: Variables .env.example")
    print("-" * 60)

    try:
        with open('.env.example', 'r') as f:
            content = f.read()

        required_vars = [
            'ENABLE_API_DOCS',
            'API_DOCS_BACKEND',
            'API_DOCS_REQUIRE_AUTH'
        ]

        all_present = True
        for var in required_vars:
            if var in content:
                print(f"  ✓ Variable '{var}' présente")
            else:
                print(f"  ✗ Variable '{var}' manquante")
                all_present = False

        print("-" * 60)
        return all_present

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        print("-" * 60)
        return False


def test_urls_modification():
    """Vérifie que urls.py a été correctement modifié"""
    print("\nTest 6: Modification de urls.py")
    print("-" * 60)

    try:
        with open('niasotac_backend/urls.py', 'r') as f:
            content = f.read()

        checks = {
            'Import modulaire': 'from niasotac_backend.config.api_docs import get_api_docs_urls',
            'Usage modulaire': 'urlpatterns += get_api_docs_urls()',
            'Pas d\'import drf_yasg direct': 'from drf_yasg.views import get_schema_view' not in content,
            'Pas de schema_view': 'schema_view = get_schema_view' not in content,
        }

        all_passed = True
        for check_name, check_result in checks.items():
            if isinstance(check_result, bool):
                status = "✓" if check_result else "✗"
                print(f"  {status} {check_name}")
                if not check_result:
                    all_passed = False
            else:
                if check_result in content:
                    print(f"  ✓ {check_name}")
                else:
                    print(f"  ✗ {check_name}")
                    all_passed = False

        print("-" * 60)
        return all_passed

    except Exception as e:
        print(f"  ✗ Erreur: {e}")
        print("-" * 60)
        return False


def main():
    """Exécute tous les tests"""
    print("=" * 60)
    print("VALIDATION DE LA CONFIGURATION API DOCS")
    print("=" * 60)
    print()

    tests = [
        test_file_structure,
        test_imports,
        test_configuration_values,
        test_required_packages,
        test_env_example,
        test_urls_modification,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Erreur dans {test_func.__name__}: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests réussis: {passed}/{total}")

    if passed == total:
        print("\n✓ Tous les tests sont passés!")
        print("\nProchaines étapes:")
        print("  1. Créez un fichier .env basé sur .env.example")
        print("  2. Installez les dépendances: pip install drf-yasg")
        print("  3. Redémarrez le serveur Django")
        print("  4. Testez /swagger/ et /redoc/ dans le navigateur")
        return 0
    else:
        print("\n✗ Certains tests ont échoué")
        print("\nVérifiez les erreurs ci-dessus et corrigez-les")
        return 1


if __name__ == '__main__':
    sys.exit(main())
