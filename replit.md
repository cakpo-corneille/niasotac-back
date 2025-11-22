# Niasotac Backend - Django REST API

## ✅ Production Status: READY

**Ce projet est maintenant prêt pour le déploiement production** avec:
- ✅ Configuration de sécurité complète (HTTPS, HSTS, cookies sécurisés, CORS strict)
- ✅ Variables d'environnement obligatoires (SECRET_KEY, ALLOWED_HOSTS, DATABASE_URL)
- ✅ Monitoring configuré (Healthcheck endpoints, Sentry, logs structurés)
- ✅ Documentation complète (README.md, DEPLOYMENT_GUIDE.md, API docs)
- ✅ Dépendances production installées (PostgreSQL, Redis, S3, Sentry)
- ✅ Entry points sécurisés (defaultent à prod.py sauf override)

**⚠️ IMPORTANT:** Le projet defaulte maintenant à `niasotac_backend.config.prod` pour tous les entry points (manage.py, wsgi.py, asgi.py, celery.py). Pour le développement local, le workflow Replit force explicitement `dev.py`.

## Overview
This is a Django REST API backend for a product showcase and e-commerce management system called Niasotac. The project provides a comprehensive admin interface for managing products, categories, promotions, newsletters, and site settings.

## Project Structure
- **niasotac_backend/**: Django project configuration
  - **config/**: Settings split into base, dev, and prod configurations
  - **urls.py**: Main URL configuration
  - **wsgi.py**: WSGI configuration for deployment
  - **celery.py**: Celery task queue configuration

- **showcase/**: Main Django app containing all business logic
  - **models/**: Data models (Product, Category, Promotion, Newsletter, etc.)
  - **admin/**: Modular admin interface with custom actions and filters
  - **services/**: Business logic layer (scoring, promotions, newsletters)
  - **api/**: REST API endpoints (v1)
  - **management/commands/**: Custom Django commands
  - **migrations/**: Database migrations

- **media/**: User-uploaded files (product images, etc.)
- **staticfiles/**: Static files (CSS, JS, admin assets)

## Tech Stack
- **Framework**: Django 4.2
- **API**: Django REST Framework with JWT authentication
- **Database**: SQLite (development), PostgreSQL-ready
- **Task Queue**: Celery with Redis backend
- **Admin**: Custom Django Admin with MPTT for category hierarchy
- **Frontend**: Configured for optional frontend integration (dist folder)

## Key Features

### Product Management
- Hierarchical categories using django-mptt
- Multiple product images with ordering
- Automatic SKU generation
- Stock tracking and status management
- Featured/Recommended algorithms based on scoring
- Product status tracking (views, clicks, engagement)

### Promotion System
- Multiple promotion types: percent, fixed amount, set price, BOGO
- Stackable/non-stackable promotions
- Category and product-specific promotions
- Usage limits per user and globally
- Scheduled promotions with date ranges

### Newsletter System
- Double opt-in subscription flow
- Template management with variable substitution
- Campaign scheduling and management
- Detailed sending logs per recipient
- Unsubscribe functionality

### Admin Interface
- Modular architecture with separate admin files
- Custom filters for stock, price ranges, engagement
- Bulk actions for common operations
- Image previews and galleries
- Performance-optimized querysets
- French language interface

## Development Setup

### Admin Access
- **Username**: admin
- **Password**: admin
- **URL**: https://[your-repl-url]/admin/

### API Endpoints (REST API v1)
L'API REST complète est maintenant disponible à `/api/v1/` avec les endpoints suivants :

#### Produits et Catégories
- **GET /api/v1/products/** - Liste paginée des produits avec filtres
  - Filtres disponibles: name, brand, category, price range, stock, featured, etc.
  - Actions: `/featured/`, `/recommended/`, `/on_sale/`
- **GET /api/v1/products/{slug}/** - Détails d'un produit (incrémente les vues)
- **POST /api/v1/products/{slug}/track_click/** - Enregistrer un clic (WhatsApp)
- **GET /api/v1/categories/** - Liste des catégories avec compteurs de produits
- **GET /api/v1/categories/tree/** - Arborescence complète des catégories
- **GET /api/v1/categories/{slug}/products/** - Produits d'une catégorie

#### Promotions
- **GET /api/v1/promotions/** - Liste des promotions avec filtres
- **GET /api/v1/promotions/active/** - Promotions actuellement actives
- **POST /api/v1/promotions/validate_code/** - Valider un code promo

#### Newsletter
- **POST /api/v1/newsletter/subscribers/** - Inscription newsletter
- **POST /api/v1/newsletter/subscribers/confirm/** - Confirmer l'email
- **POST /api/v1/newsletter/subscribers/unsubscribe/** - Se désabonner
- **GET /api/v1/newsletter/templates/** - Templates de newsletter (admin)
- **GET /api/v1/newsletter/campaigns/** - Campagnes newsletter (admin)

#### Paramètres et Services
- **GET /api/v1/settings/current/** - Paramètres actuels du site
- **GET /api/v1/services/** - Services actifs (tous pour admin)
- **GET /api/v1/social-links/** - Liens de réseaux sociaux

#### Authentification JWT
- **POST /api/token/** - Obtenir un token JWT (login)
- **POST /api/token/refresh/** - Rafraîchir le token

#### Documentation
- **Swagger UI**: `/swagger/` - Interface interactive pour tester l'API
- **ReDoc**: `/redoc/` - Documentation élégante et lisible

### Environment Variables
The project uses python-decouple for configuration. Key environment variables:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Database connection URL (optional)
- `CELERY_BROKER_URL`: Redis URL for Celery
- `CELERY_RESULT_BACKEND`: Redis URL for Celery results

### Running Locally
The Django development server is configured to run on port 5000:
```bash
python manage.py runserver 0.0.0.0:5000
```

### Database Migrations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Populate Sample Data
```bash
python manage.py populate_data
```

## Deployment

### Production Configuration
The project is configured for deployment using Gunicorn:
- Workers: 2
- Bind: 0.0.0.0:5000
- Static files: Served by WhiteNoise
- Database: Ready for PostgreSQL via DATABASE_URL

### Static Files
Static files are automatically collected and served by WhiteNoise:
```bash
python manage.py collectstatic --noinput
```

## Architecture Highlights

### Modular Admin
The admin interface is split into focused modules:
- `base.py`: Base classes and mixins
- `utils.py`: HTML display utilities
- `filters.py`: Custom list filters
- `displays.py`: Display methods for each model
- `actions.py`: Bulk actions
- Individual admin files per model

### Service Layer
Business logic is separated into services:
- `ScoringService`: Product scoring algorithms
- `PromotionService`: Promotion calculations
- `NewsletterService`: Newsletter operations

### Performance Optimization
- Custom QuerySet managers with select_related/prefetch_related
- Database indexes on frequently queried fields
- Optimized admin querysets
- N+1 query prevention

## API Documentation
- **Swagger UI**: `/swagger/`
- **ReDoc**: `/redoc/`
- **Schema**: `/swagger.json`

## Celery Tasks
Background tasks configured for:
- Newsletter sending
- Periodic score recalculation
- Scheduled promotions

To run Celery workers:
```bash
celery -A niasotac_backend worker -l info
celery -A niasotac_backend beat -l info
```

## Testing
Tests are located in `showcase/tests/`:
- API tests for products and categories
- Utilities for test data generation

Run tests with:
```bash
python manage.py test
```

## Notes
- The project is configured in French (LANGUAGE_CODE: 'fr-fr')
- Uses UTC timezone for consistency
- CORS is enabled for all origins (configure for production)
- Debug mode is enabled in development

## Recent Changes

### November 22, 2025 - Production Hardening ✅

#### PHASE 1 - Sécurité
- **prod.py sécurisé**: DEBUG forcé à False (pas de fallback), SECRET_KEY obligatoire depuis env (crash si absent)
- **ALLOWED_HOSTS strict**: Pas de wildcard accepté, validation obligatoire
- **Headers de sécurité complets**: SECURE_SSL_REDIRECT, HSTS (1 an), cookies sécurisés (Secure, HttpOnly, SameSite)
- **CORS whitelist uniquement**: CORS_ALLOW_ALL_ORIGINS=False, validation des origines obligatoire
- **Protection XSS/Clickjacking**: SECURE_BROWSER_XSS_FILTER, X_FRAME_OPTIONS='DENY'

#### PHASE 2 - Configuration
- **Dépendances production ajoutées**: dj-database-url, psycopg2-binary, django-storages, boto3, django-redis, sentry-sdk, python-json-logger
- **Entry points sécurisés**: manage.py, wsgi.py, asgi.py, celery.py defaultent à prod.py (override via DJANGO_SETTINGS_MODULE)
- **.env.example complet**: Documentation de toutes les variables env production (200+ lignes)
- **Configuration PostgreSQL/Redis**: Base de données et cache production prêts
- **S3 storage**: Configuration AWS S3 pour médias en production

#### PHASE 3 - Monitoring
- **Healthcheck endpoints**: 3 endpoints créés et testés
  - `/health/` - Check complet (database, cache, debug mode)
  - `/ready/` - Readiness probe (Kubernetes-ready)
  - `/alive/` - Liveness probe
- **Sentry configuré**: Monitoring d'erreurs avec Django/Celery integrations
- **Logging structuré**: RotatingFileHandler avec JSON optionnel, rotation 10MB, 5 backups
- **Logs directory**: Création automatique avant config pour éviter FileNotFoundError

#### PHASE 4 - Documentation
- **README.md production** (400+ lignes): Quick-start, déploiement, architecture, monitoring, sécurité, troubleshooting
- **DEPLOYMENT_GUIDE.md** (300+ lignes): Guide complet Replit/Railway/Heroku/VPS avec checklist
- **Workflow dev**: Django Dev Server configuré avec dev.py pour développement local
- **.gitignore**: Ajout de /logs/ et nettoyage

### November 18, 2025 - Initial Setup

### Replit Environment Setup
- **Python 3.11**: Installed and configured
- **Dependencies**: All requirements.txt packages installed successfully
- **Database**: SQLite database created with all migrations applied
- **Admin User**: Created default superuser (username: admin, password: admin)
- **Development Server**: Configured on port 5000 with proper host binding (0.0.0.0)
- **Deployment**: Configured for autoscale deployment using Gunicorn
- **Requirements Fix**: Fixed typo in requirements.txt (django-mppt → django-mptt)

### API REST complète implémentée
- **Serializers**: Créés pour tous les modèles avec variantes (list, detail, minimal)
  - ProductSerializer avec calcul de prix final et liens WhatsApp
  - CategorySerializer avec arborescence MPTT et breadcrumb
  - PromotionSerializer avec validation de codes promo
  - NewsletterSerializer pour gestion d'abonnements
- **Filtres avancés**: Filtrage par prix, stock, catégorie, promotions actives, etc.
- **ViewSets DRF**: Actions personnalisées (featured, recommended, on_sale, track_click)
- **Permissions**: IsAuthenticatedOrReadOnly pour la plupart des endpoints
- **URLs**: API versionnée sous `/api/v1/` avec router DRF
- **Documentation**: Swagger UI et ReDoc configurés et fonctionnels

### Corrections Replit
- Configuration CSRF pour domaines Replit dans `config/dev.py`
- Filtres corrigés pour utiliser les constantes (PROMOTION_TYPES, etc.)
- ServiceViewSet corrigé pour permettre gestion des services inactifs par admin
- Serializers alignés avec les champs réels des modèles

### Import Initial
- Fixed admin actions configuration (removed tuple syntax)
- Fixed signal sender references (changed from 'products' to 'showcase')
- Changed timezone from 'Africa/Porto-novo' to 'UTC' for compatibility
- Created migrations for showcase app
- Configured deployment with Gunicorn
- Set up development workflow on port 5000

## Support
For questions about the architecture, refer to:
- `showcase/README.md`: Product module architecture
- `showcase/admin/README.md`: Admin interface documentation
