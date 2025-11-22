# Guide de Migration - Documentation API Modulaire

Ce guide vous aide à migrer vers le nouveau système modulaire de documentation API.

## Changements Effectués

### Fichiers Ajoutés

1. **`niasotac_backend/config/api_docs.py`** - Configuration centralisée
2. **`niasotac_backend/config/API_DOCS_CONFIG.md`** - Documentation complète
3. **`manage_api_docs.py`** - Script de gestion CLI
4. **`MIGRATION_API_DOCS.md`** - Ce guide

### Fichiers Modifiés

1. **`niasotac_backend/urls.py`** - URLs simplifiées et modulaires
2. **`.env.example`** - Variables d'environnement ajoutées

### Fichiers à Supprimer (obsolètes)

1. **`niasotac_backend/config/swagger.py`** - Remplacé par `api_docs.py`

## Migration Étape par Étape

### Étape 1 : Vérifier la Configuration Actuelle

```bash
python manage_api_docs.py status
```

Vous devriez voir :
```
============================================================
CONFIGURATION DOCUMENTATION API
============================================================
Activée: True
Backend: yasg
Authentification requise: False
URLs disponibles: 4 endpoints
============================================================
```

### Étape 2 : Créer ou Mettre à Jour `.env`

Si vous n'avez pas de fichier `.env`, créez-le :

```bash
cp .env.example .env
```

Vérifiez que ces variables sont présentes :
```bash
ENABLE_API_DOCS=True
API_DOCS_BACKEND=yasg
API_DOCS_REQUIRE_AUTH=False
```

### Étape 3 : Vérifier les Dépendances

```bash
python manage_api_docs.py check
```

Si des packages manquent, installez-les :
```bash
pip install drf-yasg>=1.21.7
```

### Étape 4 : Tester les URLs

```bash
python manage_api_docs.py urls
```

Vous devriez voir :
```
URLs disponibles:
------------------------------------------------------------
  /swagger.json                   (name: schema-json)
  /swagger.yaml                   (name: schema-yaml)
  /swagger/                       (name: schema-swagger-ui)
  /redoc/                         (name: schema-redoc)
------------------------------------------------------------
Total: 4 endpoints
```

### Étape 5 : Redémarrer le Serveur

```bash
python manage.py runserver
```

### Étape 6 : Tester dans le Navigateur

Accédez à :
- http://localhost:8000/swagger/
- http://localhost:8000/redoc/

### Étape 7 : Nettoyer l'Ancien Code (optionnel)

Une fois que tout fonctionne :

```bash
# Supprimer l'ancien fichier de configuration
rm niasotac_backend/config/swagger.py

# Supprimer la référence dans git (si trackée)
git rm niasotac_backend/config/swagger.py
```

## Scénarios d'Usage

### Scénario 1 : Désactiver Temporairement

```bash
python manage_api_docs.py disable
python manage.py runserver
```

Pour réactiver :
```bash
python manage_api_docs.py enable
python manage.py runserver
```

### Scénario 2 : Changer de Backend

```bash
# Installer drf-spectacular
pip install drf-spectacular

# Basculer
python manage_api_docs.py switch spectacular
python manage.py runserver
```

### Scénario 3 : Protection par Authentification

Éditez `.env` :
```bash
API_DOCS_REQUIRE_AUTH=True
```

Redémarrez le serveur. Maintenant, seuls les utilisateurs authentifiés peuvent accéder à la documentation.

### Scénario 4 : Configuration Production

Créez `.env.prod` :
```bash
SECRET_KEY=your-super-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Documentation API désactivée en production
ENABLE_API_DOCS=False
```

Ou si vous voulez la garder avec authentification :
```bash
ENABLE_API_DOCS=True
API_DOCS_BACKEND=yasg
API_DOCS_REQUIRE_AUTH=True
```

## Avantages du Nouveau Système

### Avant (Ancien)

```python
# urls.py - Code couplé, difficile à modifier
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="NIASOTAC API",
      default_version='v1',
      ...
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    ...
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
]
```

**Problèmes :**
- Code mélangé avec les URLs principales
- Impossible de désactiver facilement
- Changement de backend = réécriture complète
- Configuration dispersée

### Après (Nouveau)

```python
# urls.py - Code propre et découplé
from niasotac_backend.config.api_docs import get_api_docs_urls

urlpatterns = [
    ...
]

# Une seule ligne pour activer/désactiver
urlpatterns += get_api_docs_urls()
```

**Avantages :**
- Configuration centralisée dans `api_docs.py`
- Activation/désactivation via `.env`
- Changement de backend sans toucher au code
- Script CLI pour gestion facile
- Documentation complète

## Résolution de Problèmes

### Erreur : "ImportError: No module named 'drf_yasg'"

**Solution :**
```bash
pip install drf-yasg
```

### Erreur : "get_api_docs_urls() returns empty list"

**Causes possibles :**
1. `ENABLE_API_DOCS=False` dans `.env`
2. Package manquant
3. Backend mal configuré

**Solution :**
```bash
python manage_api_docs.py check
```

### Les URLs ne s'affichent pas

**Solution :**
```bash
# Vérifier la config
python manage_api_docs.py status

# Vérifier les URLs chargées
python manage_api_docs.py urls

# Redémarrer le serveur
python manage.py runserver
```

### Conflit entre yasg et spectacular

**Solution :**
Désinstallez celui que vous n'utilisez pas :
```bash
pip uninstall drf-yasg
# ou
pip uninstall drf-spectacular
```

## Commandes Utiles

```bash
# Afficher la configuration actuelle
python manage_api_docs.py status

# Activer la documentation
python manage_api_docs.py enable

# Désactiver la documentation
python manage_api_docs.py disable

# Changer de backend
python manage_api_docs.py switch yasg
python manage_api_docs.py switch spectacular

# Vérifier les dépendances
python manage_api_docs.py check

# Afficher les URLs disponibles
python manage_api_docs.py urls

# Afficher l'aide
python manage_api_docs.py help
```

## Rollback (Retour en Arrière)

Si vous rencontrez des problèmes majeurs, vous pouvez revenir à l'ancien système :

1. Restaurer `niasotac_backend/urls.py` depuis git :
```bash
git checkout HEAD -- niasotac_backend/urls.py
```

2. Restaurer `niasotac_backend/config/swagger.py` :
```bash
git checkout HEAD -- niasotac_backend/config/swagger.py
```

3. Redémarrer le serveur

## Support

Si vous rencontrez des problèmes non couverts par ce guide :

1. Consultez `niasotac_backend/config/API_DOCS_CONFIG.md`
2. Vérifiez les logs Django
3. Utilisez `python manage_api_docs.py status` pour diagnostiquer

## Checklist de Migration

- [ ] Fichier `.env` créé avec les bonnes variables
- [ ] Dépendances installées (`pip install drf-yasg`)
- [ ] Configuration vérifiée (`python manage_api_docs.py status`)
- [ ] URLs disponibles (`python manage_api_docs.py urls`)
- [ ] Serveur redémarré
- [ ] Tests dans le navigateur (/swagger/ et /redoc/)
- [ ] Ancien fichier `swagger.py` supprimé (optionnel)
- [ ] Documentation lue (`API_DOCS_CONFIG.md`)

## Prochaines Étapes Recommandées

1. Testez la documentation dans votre environnement de développement
2. Configurez `.env.staging` pour l'environnement de staging
3. Configurez `.env.prod` pour la production
4. Mettez à jour votre documentation interne
5. Formez l'équipe sur les nouvelles commandes CLI
