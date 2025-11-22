# Documentation utilisateur — NIASOTAC (Backend)

Date: 2025-11-22

Ce document s'adresse à un utilisateur fonctionnel / chef de produit et décrit :
- les objectifs du backend,
- l'ensemble des fonctionnalités et services exposés côté client,
- les problèmes connus et limitations,
- le fonctionnement détaillé des principaux algorithmes (promotions, scoring, génération de slug/SKU, pricing),
- comment utiliser l'API (endpoints principaux et authentification).

Note : ce document décrit le comportement backend et les services métier exposés à la partie frontend et aux intégrateurs.

---

## 1. Objectifs du projet

NIASOTAC est une plateforme de type "vitrine / e-commerce léger" dont le backend a pour objectifs :

- Gérer un catalogue de produits structurés par catégories hiérarchiques (MPTT).
- Exposer une API REST sécurisée pour la consultation et la gestion (CRUD) des entités (produits, catégories, promotions, services, newsletters, paramètres du site).
- Fournir des mécanismes de promotion et tarification (pourcentages, montants fixes, prix fixé, BOGO).
- Suivre et scorer les produits (vues, clics WhatsApp) afin d'extraire produits vedettes et recommandés.
- Gérer des newsletters (templates, campagnes, confirmations) et l'envoi asynchrone via Celery.
- Supporter administration via Django Admin et documentation API via Swagger/ReDoc.

Audience du document : Product Owner, PM, intégrateurs front, et tout développeur client qui consomme l'API.

---

## 2. Fonctionnalités exposées côté client (liste complète)

1. Catalogue et navigation
   - Consultation des catégories hiérarchiques (arborescence), recherche et affichage des produits par catégorie.
   - Récupération de la fiche produit détaillée (description, images, stock, prix, prix barré, SKU, marque).
   - Récupération d'une miniature / image principale et de la galerie du produit.

2. Filtrage & pagination
   - Filtres par prix, catégorie, marque, disponibilité et autres attributs via `django-filter`.
   - Pagination (PageNumberPagination, `PAGE_SIZE` = 20 par défaut).

3. Promotions & codes promo
   - Récupération des promotions actives, validation d'un code promo, accessibilité des promotions par produit ou catégorie.
   - Types de promotions : pourcentage, montant fixe, prix fixé (set price), Buy X Get Y (BOGO).
   - Compatibilité empilable (stackable) vs non-empilable.

4. Statistiques produit
   - Incrémentation et affichage des compteurs de vues et des clics WhatsApp.
   - Détection de nouveaux produits (seuil configurable) et badge "nouveau".

5. Scoring et listes intelligentes
   - Endpoints pour produits mis en avant (featured), recommandés (recommended), meilleures ventes (best_sellers), produits en promo (on_sale).
   - Algorithmes internes calculent un score de vedette et de recommandation.

6. Newsletter
   - Inscription, confirmation par e-mail, déroulement de campagnes (templates + campagnes), désinscription.
   - Envoi découpé en chunks, journalisation des envois (NewsletterLog).

7. Services & liens sociaux
   - Récupération de la liste de services (Services page), liens sociaux, paramètres du site (SiteSettings) incluant numéro WhatsApp, email, adresse.

8. Authentification & administration
   - JWT auth (obtenir token via `/api/token/`, rafraîchir via `/api/token/refresh/`).
   - Django Admin disponible pour gestion des contenus (produits, promotions, newsletters, paramètres).

9. Documentation & aides
   - API documentation (Swagger UI / ReDoc) disponible via `/swagger/` et `/redoc/`.

---

## 3. Endpoints principaux (exposition publique)

Note : les chemins ci-dessous sont basés sur les routes standard et la configuration centrale (`/api/v1/`), et peuvent être complétés ou légèrement différents selon le registre des routes dans `showcase/urls.py`.

- Auth
  - `POST /api/token/` — obtenir paire token (access + refresh)
  - `POST /api/token/refresh/` — rafraîchir token

- Catégories
  - `GET /api/v1/categories/` — liste
  - `GET /api/v1/categories/{slug}/` — détail
  - `GET /api/v1/categories/tree/` — arbre complet
  - `GET /api/v1/categories/{slug}/products/` — produits d'une catégorie

- Produits
  - `GET /api/v1/products/` — liste (filtres + pagination)
  - `GET /api/v1/products/{slug}/` — détail produit
  - `GET /api/v1/products/featured/` — produits vedette
  - `GET /api/v1/products/recommended/` — produits recommandés
  - `GET /api/v1/products/on_sale/` — promotions
  - `POST /api/v1/products/{slug}/track_click/` — tracker clic WhatsApp ou similaires

- Promotions
  - `GET /api/v1/promotions/` — liste
  - `GET /api/v1/promotions/{slug}/` — détail
  - `GET /api/v1/promotions/active/` — promotions actives
  - `POST /api/v1/promotions/validate_code/` — valider un code promo

- Newsletter
  - `POST /api/v1/newsletter/subscribers/` — s'inscrire
  - `POST /api/v1/newsletter/subscribers/confirm/` — confirmer inscription par token
  - `POST /api/v1/newsletter/subscribers/unsubscribe/` — se désabonner

- Site Settings
  - `GET /api/v1/site-settings/current/` — paramètres publics (contact, WhatsApp, réseaux)

- Docs
  - `/swagger/` et `/redoc/`

---

## 4. Services backend (description fonctionnelle)

Les services métier sont organisés sous `showcase/services/`. Principaux services à connaître :

1. `PromotionService`
   - Rôle : calculer les remises applicables à un produit, déterminer la meilleure promotion, gérer la rédemption (usage tracking).
   - Fonctions clés :
     - `get_applicable_promotions(product)` : renvoie les promotions actives qui s'appliquent au produit (applies_to_all, produits ciblés, catégories ciblées).
     - `get_best_promotion(product, quantity)` : parcourt promotions applicables et retourne la promo qui offre le meilleur prix unitaire final.
     - `calculate_price_with_promotions(product, quantity)` : calcule l'effet cumulé des promotions (sépare stackable vs non-stackable, applique `set_price` puis `amount` puis `percent` pour les empilables, compare avec meilleur non-stackable).
     - `redeem_promotion(promotion, user, increment)` : incrémente l'usage (PromotionUsage) et vérifie limites globales / par utilisateur.

2. `ScoringService`
   - Rôle : calculer deux scores pour chaque produit via `ProductStatus` : `featured_score` et `recommendation_score`.
   - Utilisations : alimenter listes "vedette" et "recommandé", pour UI et tri.
   - Mécanique (détaillée plus bas) : combine vues, clics WhatsApp, nouveauté, stock, prix relatif, marge et activité récente pour produire une note pondérée.

3. `NewsletterService`
   - Rôle : envoyer emails de confirmation et campagnes.
   - Particularités : envoi par chunks (par défaut 100), journalisation (NewsletterLog), gestion d'échec par campagne, éxécution souvent asynchrone via Celery.

4. Utilitaires (`utils.py`)
   - Fonctions : `generate_unique_slug`, `generate_sku`, `format_price`, `build_whatsapp_message`, `build_whatsapp_link`, `build_absolute_url`.
   - Role côté client : `generate_sku` et `slug` impactent les URLs et références produits visibles.

5. Managers et QuerySets
   - `ProductManager`, `CategoryManager` : fournissent méthodes utiles comme `.featured()`, `.recommended()`, `.available()`, `.with_product_count()` pour simplifier les requêtes optimisées côté API.

---

## 5. Problèmes connus & limitations (côté backend)

- Configuration sensible par défaut : `CORS_ALLOW_ALL_ORIGINS = True` et fallback `SECRET_KEY` non sûr dans `base.py` (à corriger avant mise en production).
- DB par défaut : SQLite (non adaptée à la production). Recommandation : Postgres.
- Tests unitaires et d'intégration très limités (couverture insuffisante actuellement).
- Quelques incohérences de noms de champs (ex : `view_count` vs `views_count`) — risque d'erreurs côté API.
- Pas de rate-limiting par défaut sur endpoints sensibles (newsletter, validate_code) -> risque spam / brute-force.
- Stockage média local (MEDIA_ROOT) — pour production, migrer vers S3 ou un object storage.
- Monitoring basique : pas de Sentry/alerting activé par défaut dans la config actuelle.

---

## 6. Détails techniques des algorithmes (explications complètes)

### 6.1 Génération de `slug` et `sku`

- `generate_unique_slug(model_class, base_text, max_length, slug_field='slug')`
  - But : créer un slug URL-friendly unique pour un modèle.
  - Mécanique : utilise `slugify(base_text)` puis tronque pour tenir dans `max_length`. Si le slug existe déjà, ajoute `-1`, `-2`, ... jusqu'à obtenir un slug unique.
  - Remarque : operation synchrone, peut poser collisions en haute concurrence (rare pour création manuelle) — possible amélioration : check transactionnel ou suffixe avec UUID.

- `generate_sku(category_slug, model_class, prefix_length=3)`
  - But : créer un SKU unique lisible commençant par un préfixe issu de la catégorie.
  - Mécanique : prend les premiers `prefix_length` caractères du slug de la catégorie, en majuscule (ex: `ELE-00001`), récupère le dernier SKU commençant par ce préfixe, incrémente le compteur numérique.
  - Remarque : en cas de suppression ou réordering, il peut y avoir gaps ; pour concurrence, un verrou DB serait plus sûr.

### 6.2 Promotions — `PromotionService.calculate_price_with_promotions`

But : pour un produit donné (et une quantité), calculer le prix unitaire final et le montant total de la remise, en tenant compte :
- des promotions `stackable` (empilables) et non empilables,
- des différents types de promotions (percent, amount, set_price, bogo).

Algorithme détaillé :
1. Récupère les promotions applicables (filtre `is_active_now()` + `applies_to_product`).
2. Sépare en deux listes : `stackable` (empilables) et `non_stackable`.

Traitement des empilables :
- Commence par `unit_price_stack = original_price`.
- Si des `set_price` existent parmi les empilables, `unit_price_stack` devient le plus petit `set_price` trouvé (on prend le min pour donner meilleur prix possible).
- Ajoute ensuite tous les montants fixes (`amount`) cumulés : `unit_price_stack = unit_price_stack - sum(amounts)`.
- Applique ensuite chaque pourcentage (`percent`) séquentiellement :
  unit_price_stack = unit_price_stack * (1 - pct/100) pour chaque pourcentage.
- Résultat : `final_unit_stack` (quantifié au centime).

Traitement des non-empilables :
- Pour chaque non-empilable, calculer le prix final si utilisé seul (`get_discount_amount`), puis retenir le minimum (`best_non_stack_final`).

Choisir le meilleur :
- Compare `final_unit_stack` et `best_non_stack_final`, prend le plus petit des deux comme `candidate_unit`.
- Calcule `total_discount = (original_unit_price - candidate_unit) * quantity`.

Return : `(total_discount.quantize(0.01), candidate_unit.quantize(0.01))`.

Points d'attention / améliorations :
- BOGO (Buy X Get Y) dans l'implémentation actuelle calcule le montant de remise séparément (nombre d'unités gratuites * price) mais retourne le prix unitaire inchangé ; attention à la logique côté frontend pour afficher l'effet sur panier.
- Concurrence / usages : `redeem_promotion()` doit être atomic pour éviter over-redemption (utiliser `transaction.atomic()` et `select_for_update()` sur `PromotionUsage`).

### 6.3 Promotion `get_discount_amount` (dans `Promotion` model)

- `percent` : calcule discount = price * (percent/100) * qty ; final unit = price * (1 - percent/100)
- `amount` : réduit `price` d'un `unit_discount` fixe ; final unit = max(0, price - unit_discount)
- `set_price` : fixe le prix unitaire à `value`
- `bogo` : calcule groupes `group = buy_x + get_y` ; pour `qty`, calcule `free_units = (qty // group) * get_y` ; discount = free_units * price ; retourne (discount, price)

Remarque : BOGO laisse bien le prix unitaire inchangé (le gain est sur la quantité). Pour affichage panier, le front doit appliquer quantité gratuite ou afficher la remise totale.

### 6.4 Scoring produit (`ScoringService`)

Objectif : calculer deux scores (featured, recommended) à partir du `ProductStatus` et du `Product` lié.

Données utilisées :
- `view_count`, `whatsapp_click_count`, `last_viewed_at`
- `created_at` (nouveauté)
- `stock_quantity`
- `price`, `compare_at_price`, `cost_price`
- statistiques de la catégorie (prix moyen, position relative)

Formule (raccourcie) :

1. calculate_featured_score(product_status)
   - Si `force_featured` -> score = 100
   - Si `exclude_from_featured` -> score = 0
   - Ajoute pondérations :
     - Vues (last 30 days) proportionnelles à un poids (SCORE_WEIGHTS['views'])
     - Clics WhatsApp proportionnels à un poids (SCORE_WEIGHTS['whatsapp_clicks'])
     - Nouveau : bonus selon ancienneté (7 jours -> 10 points, 30 jours -> 7, etc.)
     - Stock : bonus selon quantité (>=20 -> 15 etc.)
     - Prix relatif à la catégorie : si le prix est <= 80% de la moyenne -> 10 points, etc.
     - Marge (si cost_price fournie) : plus la marge est grande, plus le score augmente (barèmes)
   - Score final arrondi ; produit vedette si score >= FEATURED_SCORE_THRESHOLD.

2. calculate_recommendation_score(product_status)
   - Si `force_recommended` -> score = 100
   - Si `exclude_from_recommended` -> score = 0
   - Base de score : engagement pondéré (vues + 3 * whatsapp_clicks)
   - Demande vs stock : calcule ratio vues/stock pour ajouter points (fort ratio => demande forte)
   - Position dans la catégorie (percentile basé sur vues) ajoute points
   - Remise : plus le discount est élevé, plus le score augmente
   - Récence : `last_viewed_at` proche => bonus
   - Score final arrondi ; produit recommandé si score >= RECOMMENDATION_SCORE_THRESHOLD.

Remarques d'implémentation :
- Les constantes `SCORE_WEIGHTS`, `RECOMMENDATION_WEIGHTS`, et seuils sont définies dans `showcase/constants.py` et paramétrables.
- `ProductStatus` supporte flags de forçage et d'exclusion pour overrides manuels.

---

## 7. Recommandations pour l'équipe produit (usage et UI expectations)

- Panier & affichage prix : afficher toujours prix original et prix final (après promotions) ainsi que montant économisé. Pour BOGO, indiquer clairement "X offert" et montant économisé.
- Promotion codes : indiquer message clair en cas d'échec (code invalide, non actif, dépasse limite d'usage).
- Expérience produit : mettre en évidence badges "Nouveau", "En promotion", "Vedette", "Recommandé" (basé sur scoring). Ne pas afficher à l'utilisateur final des détails internes (scores bruts).
- Newsletter : confirmer inscription par email avant d'ajouter aux campagnes.
- Limites de requêtes : mettre en place des protections côté client (debounce) pour éviter appels massifs (search, filter) et côté backend, rate-limiting.

---

## 8. Guide rapide pour intégrateurs (exemples d'appels)

1) Obtenir liste produits, page 1 :

```http
GET /api/v1/products/?page=1
Authorization: Bearer <ACCESS_TOKEN>  # facultatif pour lecture publique
```

2) Récupérer détail produit :

```http
GET /api/v1/products/{slug}/
```

3) Valider un code promo :

```http
POST /api/v1/promotions/validate_code/
Content-Type: application/json
{
  "code": "WINTER2025"
}
```

Réponse attendue (exemple) :
```
{ "success": true, "data": { /* promotion fields */ } }
```

4) S'inscrire à la newsletter :

```http
POST /api/v1/newsletter/subscribers/
Content-Type: application/json
{
  "email": "user@example.com",
  "name": "Marie"
}
```

Le backend enverra un e-mail de confirmation.

---

## 9. Annexes techniques et notes d'implémentation

- Documentation API auto-générée : `/swagger/` et `/redoc/`.
- Auth JWT : `rest_framework_simplejwt` (tokens courts + refresh token long).
- Tâches asynchrones : `celery` + `redis` (broker & backend) — newsletter/campaigns, tâches périodiques `django_celery_beat`.
- Fichiers statiques : `whitenoise` pour servir les `staticfiles` en production si pas de CDN.

---

## 10. Où trouver le code pertinent

- Modèles : `showcase/models/` (product.py, category.py, promotion.py)
- Serializers : `showcase/serializers.py`
- ViewSets : `showcase/views.py`
- Services métiers : `showcase/services/` (promotion_service.py, scoring_service.py, newsletter_service.py)
- Utils : `showcase/utils.py`
- Config : `niasotac_backend/config/` (base.py, dev.py, prod.py)

---

