# Configuration Modulaire de la Documentation API

Ce document explique comment gérer la documentation API (Swagger/ReDoc) de manière indépendante et modulaire.

## Architecture

```
niasotac_backend/config/
├── api_docs.py          # Configuration centralisée et modulaire
├── swagger.py           # OBSOLÈTE - à supprimer
└── API_DOCS_CONFIG.md   # Ce document
```

## Activation/Désactivation

### Via Variables d'Environnement

Créez ou modifiez votre fichier `.env` :

```bash
# Activer la documentation API (par défaut: True en dev, False en prod)
ENABLE_API_DOCS=True

# Choisir le backend ('yasg' ou 'spectacular')
API_DOCS_BACKEND=yasg

# Exiger une authentification pour accéder à la doc
API_DOCS_REQUIRE_AUTH=False
```

### Désactiver Complètement

**Méthode 1 : Variable d'environnement**
```bash
ENABLE_API_DOCS=False
```

**Méthode 2 : Dans urls.py**
Commentez simplement la ligne :
```python
# urlpatterns += get_api_docs_urls()
```

## Backends Disponibles

### DRF-YASG (par défaut)

**Avantages:**
- Interface Swagger UI complète
- Support natif de ReDoc
- Génération automatique de la documentation

**Installation:**
```bash
pip install drf-yasg>=1.21.7
```

**URLs disponibles:**
- `/swagger/` - Interface Swagger UI
- `/redoc/` - Interface ReDoc
- `/swagger.json` - Schema JSON
- `/swagger.yaml` - Schema YAML

### DRF-Spectacular

**Avantages:**
- Support OpenAPI 3.0
- Plus moderne
- Meilleure performance

**Installation:**
```bash
pip install drf-spectacular>=0.27.0
```

**URLs disponibles:**
- `/swagger/` - Interface Swagger UI
- `/redoc/` - Interface ReDoc
- `/swagger/schema/` - Schema OpenAPI

## Changement de Backend

### Passer de YASG à Spectacular

1. Installer le package:
```bash
pip install drf-spectacular
```

2. Modifier `.env`:
```bash
API_DOCS_BACKEND=spectacular
```

3. C'est tout ! Aucun changement de code nécessaire.

### Passer de Spectacular à YASG

1. Installer le package:
```bash
pip install drf-yasg
```

2. Modifier `.env`:
```bash
API_DOCS_BACKEND=yasg
```

## Désinstallation Propre

Pour retirer complètement la documentation API :

### Étape 1 : Désactiver

```bash
# Dans .env
ENABLE_API_DOCS=False
```

### Étape 2 : Retirer les dépendances

```bash
pip uninstall drf-yasg drf-spectacular
```

### Étape 3 : Nettoyer le code (optionnel)

Dans `urls.py`, commentez ou supprimez :
```python
# from niasotac_backend.config.api_docs import get_api_docs_urls
# urlpatterns += get_api_docs_urls()
```

Dans `requirements.txt`, supprimez :
```
drf-yasg>=1.21.7
# ou
drf-spectacular>=0.27.0
```

### Étape 4 : Supprimer le fichier obsolète

```bash
rm niasotac_backend/config/swagger.py
```

## Configuration Avancée

### Personnalisation de YASG

Éditez `api_docs.py` section `YASG_INFO` et `YASG_SETTINGS`:

```python
YASG_INFO = {
    'title': "Mon API",
    'default_version': 'v2',
    'description': "Ma description personnalisée",
    ...
}
```

### Personnalisation de Spectacular

Éditez `api_docs.py` section `SPECTACULAR_SETTINGS`:

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Mon API',
    'VERSION': '2.0.0',
    ...
}
```

### Restreindre l'accès

Pour exiger une authentification :

```bash
# Dans .env
API_DOCS_REQUIRE_AUTH=True
```

## Diagnostic

### Vérifier la configuration actuelle

Dans un shell Django :

```python
from niasotac_backend.config.api_docs import print_config
print_config()
```

Affichera :
```
============================================================
CONFIGURATION DOCUMENTATION API
============================================================
Activée: True
Backend: yasg
Authentification requise: False
URLs disponibles: 4 endpoints
============================================================

Endpoints disponibles:
  - /swagger.json
  - /swagger.yaml
  - /swagger/
  - /redoc/
```

### Vérifier les URLs chargées

```python
from niasotac_backend.config.api_docs import get_api_docs_urls
urls = get_api_docs_urls()
print(f"Nombre d'URLs: {len(urls)}")
```

### Vérifier le backend actif

```python
from niasotac_backend.config.api_docs import get_backend_name
print(f"Backend actif: {get_backend_name()}")
```

## Migration depuis l'ancienne configuration

Si vous aviez l'ancienne configuration avec `swagger.py` :

### Avant (ancien système)
```python
# Dans urls.py
from niasotac_backend.config.swagger import get_swagger_urls
urlpatterns += get_swagger_urls()
```

### Après (nouveau système)
```python
# Dans urls.py
from niasotac_backend.config.api_docs import get_api_docs_urls
urlpatterns += get_api_docs_urls()
```

### Fichiers à supprimer
- `niasotac_backend/config/swagger.py` (obsolète)

## Exemples de Configuration

### Développement

```bash
# .env.dev
ENABLE_API_DOCS=True
API_DOCS_BACKEND=yasg
API_DOCS_REQUIRE_AUTH=False
```

### Production

```bash
# .env.prod
ENABLE_API_DOCS=False
# ou si vous voulez la garder en prod avec auth
ENABLE_API_DOCS=True
API_DOCS_BACKEND=yasg
API_DOCS_REQUIRE_AUTH=True
```

### Test/Staging

```bash
# .env.staging
ENABLE_API_DOCS=True
API_DOCS_BACKEND=spectacular
API_DOCS_REQUIRE_AUTH=False
```

## Troubleshooting

### Erreur : "drf-yasg n'est pas installé"

**Solution :**
```bash
pip install drf-yasg
```

### Erreur : "drf-spectacular n'est pas installé"

**Solution :**
```bash
pip install drf-spectacular
```

### Les URLs ne s'affichent pas

**Vérifications :**
1. `ENABLE_API_DOCS=True` dans `.env`
2. Le package correspondant est installé
3. Redémarrer le serveur Django

### Conflit entre les deux backends

**Solution :**
Désinstallez celui que vous n'utilisez pas :
```bash
pip uninstall drf-yasg
# ou
pip uninstall drf-spectacular
```

## Bonnes Pratiques

1. **En production** : Désactivez ou protégez par authentification
2. **En développement** : Gardez activé pour faciliter le travail
3. **Tests** : Utilisez `ENABLE_API_DOCS=False` pour accélérer les tests
4. **Documentation** : Choisissez un backend et restez-y pour la cohérence

## Support

Pour toute question ou problème :
- Consultez ce document
- Vérifiez les logs Django
- Utilisez `print_config()` pour diagnostiquer
