# 🚀 NIASOTAC Backend API

API REST Django pour plateforme de showcase de produits avec système de promotions automatisées, catégories hiérarchiques, et newsletter.

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![DRF](https://img.shields.io/badge/DRF-3.16-red.svg)](https://www.django-rest-framework.org/)
[![Production Ready](https://img.shields.io/badge/Production-Ready-success.svg)]()

## ✨ Fonctionnalités

### Core Features
- 🏪 **Gestion de produits** avec images, catégories hiérarchiques (django-mptt)
- 🏷️ **Promotions automatiques** avec scoring personnalisé et règles métier
- 📧 **Newsletter** avec double opt-in, templates personnalisés, et envoi asynchrone (Celery)
- 🔐 **Authentification JWT** avec refresh tokens
- 📊 **API RESTful** complète avec pagination, filtres, recherche
- 📚 **Documentation API** auto-générée (Swagger/ReDoc)

### Architecture
- ⚡ **Performance:** Cache Redis, optimisations DB, pagination
- 🔒 **Sécurité:** HTTPS forcé, CORS strict, headers sécurisés, validation complète
- 📈 **Monitoring:** Healthcheck endpoints, Sentry, logs structurés JSON
- 🎯 **Production Ready:** Configuration env-based, S3 storage, Celery workers

---

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- PostgreSQL
- Redis
- AWS S3 (optionnel, recommandé pour production)

### Installation Locale

```bash
# 1. Cloner le repo
git clone https://github.com/votre-org/niasotac-backend.git
cd niasotac-backend

# 2. Créer environnement virtuel
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Configuration environnement
cp .env.example .env
# Éditer .env avec vos valeurs

# 5. Export settings module (dev)
export DJANGO_SETTINGS_MODULE=niasotac_backend.config.dev

# 6. Migrations
python manage.py migrate

# 7. Créer superuser
python manage.py createsuperuser

# 8. Collecter fichiers statiques (optionnel en dev)
python manage.py collectstatic --noinput

# 9. Lancer le serveur
python manage.py runserver
```

**API accessible à:** http://localhost:8000  
**Admin Django:** http://localhost:8000/admin/  
**Documentation API:** http://localhost:8000/swagger/

---

## 📦 Déploiement Production

### ⚠️ IMPORTANT: Configuration Production

Le projet **defaulte automatiquement à la configuration production** (`niasotac_backend.config.prod`) sauf si vous spécifiez explicitement `DJANGO_SETTINGS_MODULE`.

**Pour le développement local uniquement:**
```bash
export DJANGO_SETTINGS_MODULE=niasotac_backend.config.dev
```

**En production (par défaut):**
```bash
# Aucun export nécessaire, prod.py est utilisé automatiquement
# Ou explicitement:
export DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
```

### Variables d'Environnement OBLIGATOIRES

Avant tout déploiement, **VOUS DEVEZ** configurer:

```bash
# Critiques
SECRET_KEY=<généré-aléatoirement-50-chars>
ALLOWED_HOSTS=api.votre-domaine.com,votre-domaine.com
DATABASE_URL=postgresql://user:pass@host:5432/db

# Sécurité
CORS_ALLOWED_ORIGINS=https://votre-frontend.com
CSRF_TRUSTED_ORIGINS=https://votre-frontend.com

# Services
REDIS_URL=redis://host:6379/0
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_STORAGE_BUCKET_NAME=xxx

# Email
EMAIL_HOST_USER=xxx
EMAIL_HOST_PASSWORD=xxx
```

📘 **Voir `.env.example` pour la liste complète et documentation.**

### Déploiement Rapide

#### Replit
```bash
# 1. Créer PostgreSQL database dans Replit
# 2. Ajouter secrets dans l'onglet "Secrets"
# 3. Migrations et collectstatic
python manage.py migrate
python manage.py collectstatic --noinput
# 4. Déployer
gunicorn --bind 0.0.0.0:5000 --workers 4 niasotac_backend.wsgi:application
```

#### Railway / Heroku
```bash
# Railway
railway init
railway add postgresql redis
railway up

# Heroku
heroku create
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
```

#### VPS / Serveur dédié
Voir **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** pour instructions complètes.

---

## 🏗️ Architecture

### Structure du Projet
```
niasotac-backend/
├── niasotac_backend/          # Configuration Django
│   ├── config/
│   │   ├── base.py           # Settings communs
│   │   ├── dev.py            # Settings développement
│   │   └── prod.py           # Settings production (DEFAULT)
│   ├── wsgi.py               # WSGI entry point
│   └── celery.py             # Celery config
├── showcase/                  # App principale
│   ├── models/               # Modèles DB
│   ├── serializers/          # DRF Serializers
│   ├── views/                # API Views
│   ├── tasks.py              # Celery tasks (newsletter, scoring)
│   └── healthcheck.py        # Endpoints monitoring
├── .env.example              # Template variables env
├── requirements.txt          # Dépendances Python
├── DEPLOYMENT_GUIDE.md       # Guide déploiement complet
└── README.md                 # Ce fichier
```

### Modèles Principaux
- **Category** (MPTT): Catégories hiérarchiques
- **Product**: Produits avec images S3
- **Promotion**: Règles de promotion et scoring
- **Subscriber**: Newsletter avec double opt-in
- **EmailTemplate**: Templates newsletters personnalisables

### Technologies
- **Framework:** Django 4.2 LTS, Django REST Framework
- **Base de données:** PostgreSQL (production), SQLite (dev)
- **Cache & Queue:** Redis, Celery
- **Storage:** AWS S3 (médias), Whitenoise (static)
- **Monitoring:** Sentry, Healthcheck endpoints
- **Auth:** JWT (djangorestframework-simplejwt)

---

## 🔍 Endpoints Principaux

### API v1 (`/api/v1/`)
- `GET /products/` - Liste produits (filtres, recherche, pagination)
- `GET /products/{id}/` - Détail produit
- `GET /categories/` - Arbre catégories
- `GET /promotions/active/` - Promotions actives
- `POST /newsletter/subscribe/` - Inscription newsletter
- `GET /newsletter/confirm/{token}/` - Confirmation email

### Monitoring
- `GET /health/` - Healthcheck complet (DB, cache, status)
- `GET /ready/` - Readiness probe (Kubernetes)
- `GET /alive/` - Liveness probe

### Documentation
- `GET /swagger/` - Documentation Swagger UI
- `GET /redoc/` - Documentation ReDoc

### Admin & Auth
- `POST /api/token/` - Obtenir JWT token
- `POST /api/token/refresh/` - Refresh token
- `GET /admin/` - Interface admin Django

---

## 📊 Monitoring & Santé

### Healthcheck
```bash
curl https://api.votre-domaine.com/health/
```

Réponse attendue:
```json
{
  "status": "healthy",
  "checks": {
    "database": "healthy",
    "cache": "healthy",
    "debug_mode": "OFF"
  },
  "version": "1.0.0",
  "python_version": "3.11.x"
}
```

### Logs
- **Console:** Logs temps réel (stdout)
- **Fichier:** `logs/production.log` (rotation 10MB, 5 backups)
- **Format:** JSON structuré (optionnel via `LOG_JSON=True`)
- **Sentry:** Erreurs et performances (si configuré)

---

## 🔐 Sécurité

### Mesures Implémentées
✅ DEBUG forcé à False en production (pas de fallback)  
✅ SECRET_KEY obligatoire depuis env (crash si absent)  
✅ ALLOWED_HOSTS strict (pas de wildcard)  
✅ HTTPS forcé (SECURE_SSL_REDIRECT)  
✅ HSTS activé (1 an)  
✅ Cookies sécurisés (Secure, HttpOnly, SameSite)  
✅ CORS whitelist uniquement  
✅ Headers XSS, Clickjacking, Content-Type  
✅ Validation complète des entrées  
✅ Rate limiting (optionnel, recommandé)  

### Checklist Avant Production
- [ ] SECRET_KEY unique et complexe (50+ chars)
- [ ] DATABASE_URL vers PostgreSQL (pas SQLite)
- [ ] ALLOWED_HOSTS configuré (pas de `*`)
- [ ] CORS_ALLOWED_ORIGINS restrictif
- [ ] S3 configuré (USE_S3=True)
- [ ] Redis configuré (REDIS_URL)
- [ ] Email SMTP configuré
- [ ] HTTPS/SSL activé
- [ ] Sentry configuré (recommandé)
- [ ] Backups DB automatisés

---

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests avec coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Rapport HTML dans htmlcov/

# Tests spécifiques
python manage.py test showcase.tests.test_newsletter
python manage.py test showcase.tests.test_promotions
```

**Objectif coverage:** >80%

---

## 📚 Documentation Complémentaire

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Guide déploiement complet (Replit, Railway, Heroku, VPS)
- **[API_DOCUMENTATION_FRONTEND.md](./API_DOCUMENTATION_FRONTEND.md)** - Guide API pour développeurs frontend (500+ lignes)
- **[ARCHITECTURE_FONCTIONNELLE.md](./ARCHITECTURE_FONCTIONNELLE.md)** - Architecture métier et logique business (300+ lignes)
- **Swagger UI:** `/swagger/` - Documentation interactive en live

---

## 🛠️ Développement

### Structure des Settings
Le projet utilise 3 fichiers de configuration:

1. **`base.py`** - Configuration commune (apps, middleware, etc.)
2. **`dev.py`** - Développement (DEBUG=True, SQLite, CORS permissif)
3. **`prod.py`** - Production (sécurisé, PostgreSQL, CORS strict) **← DEFAULT**

### Commandes Utiles

```bash
# Créer migrations
python manage.py makemigrations

# Appliquer migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Collecter fichiers statiques
python manage.py collectstatic

# Shell Django
python manage.py shell

# Lancer Celery worker
celery -A niasotac_backend worker -l info

# Lancer Celery beat (tâches périodiques)
celery -A niasotac_backend beat -l info
```

### Workflow Git
```bash
# Développer sur une branche feature
git checkout -b feature/nouvelle-fonctionnalite

# Tests avant commit
python manage.py test
python manage.py check --deploy

# Commit et push
git add .
git commit -m "feat: description"
git push origin feature/nouvelle-fonctionnalite
```

---

## 🐛 Troubleshooting

### Problème: "SECRET_KEY non défini"
**Solution:** Définir `SECRET_KEY` dans .env ou via `export SECRET_KEY="..."`

### Problème: CORS error frontend
**Solution:** Ajouter l'origine frontend dans `CORS_ALLOWED_ORIGINS`

### Problème: Images ne s'affichent pas
**Solution:** Vérifier configuration S3 ou mettre `USE_S3=False` (dev uniquement)

### Problème: Celery ne démarre pas
**Solution:** Vérifier que Redis est accessible (`redis-cli ping`)

📘 **Voir [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) section Troubleshooting pour plus de solutions.**

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/votre-org/niasotac-backend/issues)
- **Documentation API:** `/swagger/`
- **Email:** support@niasotac.com

---

## 📝 License

Propriétaire - Tous droits réservés © 2024 Niasotac

---

## 🎯 Statut du Projet

✅ **Production Ready**  
✅ Sécurité validée  
✅ Configuration env-based  
✅ Monitoring configuré  
✅ Documentation complète  
✅ Tests unitaires  
✅ Healthcheck endpoints  

**Dernière mise à jour:** 22 novembre 2025  
**Version:** 1.0.0  
**Maintenu par:** Équipe Niasotac
