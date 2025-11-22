# 🚀 GUIDE DE DÉPLOIEMENT - NIASOTAC BACKEND

## TABLE DES MATIÈRES
1. [Pré-requis](#pré-requis)
2. [Configuration de l'environnement](#configuration-de-lenvironnement)
3. [Déploiement sur Replit](#déploiement-sur-replit)
4. [Déploiement sur Railway/Heroku](#déploiement-sur-railwayheroku)
5. [Déploiement sur VPS](#déploiement-sur-vps)
6. [Post-déploiement](#post-déploiement)
7. [Troubleshooting](#troubleshooting)

---

## PRÉ-REQUIS

### Services Externes Requis

#### 1. **Base de données PostgreSQL** ✅ OBLIGATOIRE
- [ ] Créer une base PostgreSQL (via Replit, Railway, Heroku, ou provider cloud)
- [ ] Noter le `DATABASE_URL`
- [ ] Vérifier que SSL est activé

#### 2. **Redis** ✅ OBLIGATOIRE (pour Celery)
- [ ] Créer une instance Redis
- [ ] Noter le `REDIS_URL`

#### 3. **AWS S3** ✅ RECOMMANDÉ (stockage médias)
- [ ] Créer un compte AWS
- [ ] Créer un bucket S3 (ex: `niasotac-media-production`)
- [ ] Créer un utilisateur IAM avec accès S3
- [ ] Noter `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`

#### 4. **Service Email SMTP** ✅ OBLIGATOIRE (newsletter)
Choisir un provider:
- Gmail (gratuit, limité à 500 emails/jour)
- SendGrid (gratuit jusqu'à 100 emails/jour)
- Mailgun
- Amazon SES

#### 5. **Sentry** ❌ OPTIONNEL (monitoring erreurs)
- [ ] Créer un compte sur sentry.io
- [ ] Créer un projet Django
- [ ] Noter le `SENTRY_DSN`

---

## CONFIGURATION DE L'ENVIRONNEMENT

### 1. Copier .env.example en .env

```bash
cp .env.example .env
```

### 2. Remplir les variables OBLIGATOIRES

Éditer `.env` avec vos valeurs:

```bash
# SECRET_KEY - Générer une nouvelle clé
# Commande: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=votre-clé-générée-ici

# Debug - TOUJOURS False en production
DEBUG=False

# Domaines autorisés
ALLOWED_HOSTS=api.votre-domaine.com,votre-domaine.com

# Base de données (fournie par votre provider)
DATABASE_URL=postgresql://user:password@host:port/database

# CORS - Domaines frontend autorisés
CORS_ALLOWED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://votre-domaine.com,https://www.votre-domaine.com

# Redis
REDIS_URL=redis://host:port/0

# S3
USE_S3=True
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_STORAGE_BUCKET_NAME=votre-bucket

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@votre-domaine.com

# Sentry (optionnel)
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

### 3. Exporter DJANGO_SETTINGS_MODULE

```bash
export DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
```

---

## DÉPLOIEMENT SUR REPLIT

### Étape 1: Configuration de la base de données

```bash
# Créer une PostgreSQL database via Replit Database
# DATABASE_URL sera automatiquement disponible
```

### Étape 2: Variables d'environnement

Dans l'onglet "Secrets" de Replit, ajouter:

```
SECRET_KEY=généré-automatiquement-ou-custom
ALLOWED_HOSTS=votre-repl-url.replit.dev
CORS_ALLOWED_ORIGINS=https://votre-repl-url.replit.dev
CSRF_TRUSTED_ORIGINS=https://votre-repl-url.replit.dev
USE_S3=True
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_STORAGE_BUCKET_NAME=xxx
EMAIL_HOST_USER=xxx
EMAIL_HOST_PASSWORD=xxx
SENTRY_DSN=xxx
DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
```

### Étape 3: Déploiement

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Migrations
python manage.py migrate

# 3. Créer un superuser
python manage.py createsuperuser

# 4. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 5. Lancer le serveur
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 niasotac_backend.wsgi:application
```

### Étape 4: Worker Celery (optionnel)

Créer un deuxième Repl ou utiliser un service de worker:

```bash
celery -A niasotac_backend worker -l info
```

---

## DÉPLOIEMENT SUR RAILWAY/HEROKU

### Railway

#### 1. Créer un nouveau projet

```bash
railway init
```

#### 2. Ajouter PostgreSQL et Redis

```bash
railway add postgresql
railway add redis
```

#### 3. Variables d'environnement

```bash
# Railway détecte automatiquement DATABASE_URL et REDIS_URL
railway variables set SECRET_KEY="votre-secret-key"
railway variables set ALLOWED_HOSTS="votre-app.railway.app"
railway variables set DJANGO_SETTINGS_MODULE="niasotac_backend.config.prod"
railway variables set USE_S3="True"
# ... autres variables
```

#### 4. Déployer

```bash
railway up
```

### Heroku

#### 1. Créer l'app

```bash
heroku create niasotac-api
```

#### 2. Ajouter addons

```bash
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
```

#### 3. Variables d'environnement

```bash
heroku config:set SECRET_KEY="votre-secret-key"
heroku config:set ALLOWED_HOSTS="niasotac-api.herokuapp.com"
heroku config:set DJANGO_SETTINGS_MODULE="niasotac_backend.config.prod"
heroku config:set USE_S3="True"
# ... autres variables
```

#### 4. Déployer

```bash
git push heroku main
```

#### 5. Migrations

```bash
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## DÉPLOIEMENT SUR VPS (Ubuntu/Debian)

### Prérequis Serveur

```bash
# Mise à jour
sudo apt update && sudo apt upgrade -y

# Installer Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Installer PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Installer Redis
sudo apt install redis-server -y

# Installer Nginx
sudo apt install nginx -y
```

### 1. Créer l'utilisateur et le projet

```bash
# Créer utilisateur
sudo adduser niasotac
sudo usermod -aG sudo niasotac

# Se connecter
su - niasotac

# Cloner le projet
git clone https://github.com/votre-repo/niasotac-backend.git
cd niasotac-backend
```

### 2. Environnement virtuel et dépendances

```bash
# Créer venv
python3.11 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

### 3. Configurer PostgreSQL

```bash
# Créer base et utilisateur
sudo -u postgres psql
```

```sql
CREATE DATABASE niasotac_db;
CREATE USER niasotac_user WITH PASSWORD 'mot-de-passe-fort';
ALTER ROLE niasotac_user SET client_encoding TO 'utf8';
ALTER ROLE niasotac_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE niasotac_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE niasotac_db TO niasotac_user;
\q
```

### 4. Configuration .env

```bash
nano .env
```

Copier le contenu de .env.example et remplir.

### 5. Migrations et collectstatic

```bash
export DJANGO_SETTINGS_MODULE=niasotac_backend.config.prod
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 6. Gunicorn service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=Gunicorn daemon for Niasotac Backend
After=network.target

[Service]
User=niasotac
Group=www-data
WorkingDirectory=/home/niasotac/niasotac-backend
EnvironmentFile=/home/niasotac/niasotac-backend/.env
ExecStart=/home/niasotac/niasotac-backend/venv/bin/gunicorn \
          --access-logfile - \
          --workers 4 \
          --bind unix:/home/niasotac/niasotac-backend/gunicorn.sock \
          niasotac_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 7. Nginx

```bash
sudo nano /etc/nginx/sites-available/niasotac
```

```nginx
server {
    listen 80;
    server_name api.votre-domaine.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /home/niasotac/niasotac-backend/staticfiles/;
    }
    
    location /media/ {
        alias /home/niasotac/niasotac-backend/media/;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/home/niasotac/niasotac-backend/gunicorn.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/niasotac /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.votre-domaine.com
```

### 9. Celery Worker

```bash
sudo nano /etc/systemd/system/celery.service
```

```ini
[Unit]
Description=Celery Worker for Niasotac
After=network.target redis.service

[Service]
Type=forking
User=niasotac
Group=www-data
WorkingDirectory=/home/niasotac/niasotac-backend
EnvironmentFile=/home/niasotac/niasotac-backend/.env
ExecStart=/home/niasotac/niasotac-backend/venv/bin/celery -A niasotac_backend worker -l info

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start celery
sudo systemctl enable celery
```

---

## POST-DÉPLOIEMENT

### 1. Vérifier le healthcheck

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

### 2. Tester les endpoints

```bash
# Liste des produits
curl https://api.votre-domaine.com/api/v1/products/

# Documentation API
open https://api.votre-domaine.com/swagger/
```

### 3. Créer les données de test (optionnel)

```bash
python manage.py populate_data
```

### 4. Configurer les tâches Celery Beat

```bash
python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# Nettoyage abonnés non confirmés (tous les jours à 3h)
schedule, created = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.DAYS,
)

PeriodicTask.objects.get_or_create(
    interval=schedule,
    name='Nettoyage abonnés newsletter',
    task='showcase.tasks.cleanup_unconfirmed_subscribers',
)
```

### 5. Monitoring

#### Vérifier Sentry

Provoquer une erreur volontaire et vérifier qu'elle apparaît dans Sentry.

#### Configurer des alertes

- [ ] Alerte si healthcheck échoue
- [ ] Alerte si erreur 500
- [ ] Alerte si base de données indisponible

---

## TROUBLESHOOTING

### Problème: "SECRET_KEY non défini"

**Cause:** Variable d'environnement manquante

**Solution:**
```bash
# Vérifier
echo $SECRET_KEY

# Si vide, exporter
export SECRET_KEY="votre-clé"

# Ou ajouter au .env et sourcer
source .env
```

### Problème: "ALLOWED_HOSTS invalid"

**Cause:** Domaine non dans ALLOWED_HOSTS

**Solution:**
```bash
# Ajouter votre domaine
export ALLOWED_HOSTS="votre-domaine.com,www.votre-domaine.com"
```

### Problème: "CORS error" dans le frontend

**Cause:** Origine non autorisée

**Solution:**
```bash
# Ajouter l'origine frontend
export CORS_ALLOWED_ORIGINS="https://votre-frontend.com"
export CSRF_TRUSTED_ORIGINS="https://votre-frontend.com"
```

### Problème: Images ne s'affichent pas

**Cause:** S3 non configuré

**Solution:**
```bash
# Vérifier S3
export USE_S3=True
export AWS_ACCESS_KEY_ID="xxx"
export AWS_SECRET_ACCESS_KEY="xxx"
export AWS_STORAGE_BUCKET_NAME="xxx"

# Ou utiliser stockage local (dev uniquement)
export USE_S3=False
```

### Problème: Emails ne partent pas

**Cause:** SMTP mal configuré

**Solution:**
```bash
# Pour Gmail, créer un "mot de passe d'application"
# Paramètres Gmail → Sécurité → Validation en 2 étapes → Mots de passe d'applications

export EMAIL_HOST_USER="votre-email@gmail.com"
export EMAIL_HOST_PASSWORD="mot-de-passe-application"
```

### Problème: Celery ne démarre pas

**Cause:** Redis non accessible

**Solution:**
```bash
# Vérifier Redis
redis-cli ping
# Doit retourner: PONG

# Vérifier REDIS_URL
echo $REDIS_URL

# Tester Celery
celery -A niasotac_backend worker -l info
```

### Problème: Migration échoue

**Cause:** Base de données non accessible

**Solution:**
```bash
# Tester la connexion
python manage.py dbshell

# Vérifier DATABASE_URL
echo $DATABASE_URL

# Forcer les migrations
python manage.py migrate --fake-initial
```

---

## CHECKLIST FINALE

### Avant de passer en production

- [ ] SECRET_KEY unique et sécurisée
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS correctement configuré
- [ ] DATABASE_URL pointe vers PostgreSQL (pas SQLite)
- [ ] REDIS_URL configuré
- [ ] S3 configuré pour les médias
- [ ] CORS_ALLOWED_ORIGINS restrictif
- [ ] HTTPS activé (SSL/TLS)
- [ ] Sentry configuré pour monitoring
- [ ] Healthcheck accessible
- [ ] Migrations appliquées
- [ ] Superuser créé
- [ ] Fichiers statiques collectés
- [ ] Celery worker démarre
- [ ] Emails de test fonctionnent
- [ ] Backups base de données configurés
- [ ] Logs centralisés configurés

### Performance

- [ ] Gunicorn avec 4+ workers
- [ ] Redis cache activé
- [ ] CDN configuré pour static/media (optionnel)
- [ ] Compression Gzip activée (Nginx)

### Sécurité

- [ ] Firewall configuré
- [ ] Rate limiting activé
- [ ] Headers de sécurité activés (HSTS, XSS, etc.)
- [ ] Secrets jamais committés dans Git
- [ ] Accès SSH par clé uniquement (VPS)

---

**Dernière mise à jour:** 22 novembre 2024
**Version:** 1.0
**Maintenu par:** Équipe Niasotac
