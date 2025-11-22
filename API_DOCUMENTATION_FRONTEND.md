# 📘 DOCUMENTATION API - GUIDE DÉVELOPPEUR FRONTEND

## TABLE DES MATIÈRES
1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Format des réponses](#format-des-réponses)
4. [Endpoints Disponibles](#endpoints-disponibles)
   - [Produits](#produits)
   - [Catégories](#catégories)
   - [Promotions](#promotions)
   - [Newsletter](#newsletter)
   - [Services et Paramètres](#services-et-paramètres)
5. [Filtres et Recherche](#filtres-et-recherche)
6. [Gestion des Erreurs](#gestion-des-erreurs)
7. [Checklist Développement](#checklist-développement)

---

## VUE D'ENSEMBLE

### Qu'est-ce que cette API ?

Cette API vous permet de créer un site e-commerce dynamique sans jamais toucher au code backend. Elle gère automatiquement:
- **Le catalogue produits** avec catégories hiérarchiques
- **Les promotions** avec calcul automatique des meilleurs prix
- **Le système de recommandation** qui met en avant les produits pertinents
- **La newsletter** avec confirmation par email
- **Les paramètres du site** (coordonnées, réseaux sociaux, etc.)

### URL de base

```
Développement: http://localhost:5000/api/v1/
Production: https://votre-domaine.com/api/v1/
```

### Format de données

- **Envoi:** JSON (Content-Type: application/json)
- **Réception:** JSON
- **Encodage:** UTF-8
- **Dates:** Format ISO 8601 (ex: "2024-11-22T14:30:00Z")

---

## AUTHENTIFICATION

### Obtenir un token JWT

**Endpoint:** `POST /api/token/`

**Utilisation:** Pour les actions d'administration (création, modification, suppression)

**Requête:**
```json
{
  "username": "admin@example.com",
  "password": "motdepasse"
}
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Utilisation du token:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Rafraîchir le token

**Endpoint:** `POST /api/token/refresh/`

**Requête:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Note:** Les endpoints de consultation (GET) sont accessibles sans authentification.

---

## FORMAT DES RÉPONSES

### Liste de ressources

**Structure standard:**
```json
{
  "count": 42,
  "next": "http://api.com/products/?page=2",
  "previous": null,
  "results": [
    { ... },
    { ... }
  ]
}
```

### Ressource unique

```json
{
  "id": 1,
  "name": "Produit exemple",
  ...
}
```

### Pagination

Par défaut: 20 éléments par page

**Paramètres:**
- `?page=2` - Page spécifique
- `?page_size=50` - Nombre d'éléments par page (max 100)

---

## ENDPOINTS DISPONIBLES

## PRODUITS

### 📋 Lister les produits

**Endpoint:** `GET /api/v1/products/`

**Usage:** Afficher tous les produits (page catalogue, recherche, filtres)

**Réponse:**
```json
{
  "count": 156,
  "next": "http://api.com/api/v1/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Smartphone Galaxy Pro",
      "slug": "smartphone-galaxy-pro",
      "brand": "Samsung",
      "price": "599.00",
      "compare_at_price": "799.00",
      "final_price": "599.00",
      "has_discount": true,
      "category": 5,
      "category_name": "Smartphones",
      "main_image": "http://api.com/media/products/galaxy-pro.jpg",
      "in_stock": true,
      "is_featured": true,
      "is_recommended": true,
      "short_description": "Le meilleur smartphone de l'année",
      "created_at": "2024-11-01T10:00:00Z"
    }
  ]
}
```

**Champs importants:**

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Identifiant unique du produit |
| `name` | String | Nom du produit |
| `slug` | String | URL-friendly (pour les liens) |
| `brand` | String | Marque du produit |
| `price` | Decimal | Prix de base |
| `compare_at_price` | Decimal | Prix barré (si promo) |
| `final_price` | Decimal | **Prix final après calcul automatique des promotions** |
| `has_discount` | Boolean | Le produit a une réduction active |
| `main_image` | URL | Image principale (URL complète) |
| `in_stock` | Boolean | Produit disponible |
| `is_featured` | Boolean | Badge "À la une" (score ≥ 70) |
| `is_recommended` | Boolean | Badge "Recommandé" (score ≥ 50) |

**Filtres disponibles:**

```http
# Recherche par nom, marque, description, SKU
GET /api/v1/products/?search=samsung

# Filtrer par catégorie (ID ou slug)
GET /api/v1/products/?category=5
GET /api/v1/products/?category_slug=smartphones

# Filtrer par prix
GET /api/v1/products/?min_price=100&max_price=500

# Filtrer par stock
GET /api/v1/products/?in_stock=true

# Filtrer par badges
GET /api/v1/products/?is_featured=true
GET /api/v1/products/?is_recommended=true

# Filtrer avec promotions
GET /api/v1/products/?has_discount=true

# Filtrer par marque
GET /api/v1/products/?brand=Samsung

# Filtrer par date
GET /api/v1/products/?created_after=2024-01-01

# Tri (nom, prix, date, vues, score)
GET /api/v1/products/?ordering=price              # Prix croissant
GET /api/v1/products/?ordering=-price             # Prix décroissant
GET /api/v1/products/?ordering=-created_at        # Plus récents
GET /api/v1/products/?ordering=-views_count       # Plus consultés
GET /api/v1/products/?ordering=-featured_score    # Meilleur score

# Combiner plusieurs filtres
GET /api/v1/products/?category_slug=smartphones&min_price=300&max_price=800&is_featured=true&ordering=-price
```

**Exemple d'utilisation React:**

```javascript
// Récupérer les produits "À la une" triés par score
const fetchFeaturedProducts = async () => {
  const response = await fetch(
    'http://localhost:5000/api/v1/products/?is_featured=true&ordering=-featured_score'
  );
  const data = await response.json();
  return data.results;
};

// Recherche de produits
const searchProducts = async (query) => {
  const response = await fetch(
    `http://localhost:5000/api/v1/products/?search=${encodeURIComponent(query)}`
  );
  const data = await response.json();
  return data.results;
};
```

---

### 📄 Détails d'un produit

**Endpoint:** `GET /api/v1/products/{id}/` ou `GET /api/v1/products/{slug}/`

**Usage:** Afficher la fiche produit complète

**Réponse:**
```json
{
  "id": 1,
  "name": "Smartphone Galaxy Pro",
  "slug": "smartphone-galaxy-pro",
  "sku": "SMRT-GAL-001",
  "barcode": "1234567890123",
  "brand": "Samsung",
  "category": {
    "id": 5,
    "name": "Smartphones",
    "slug": "smartphones",
    "level": 2,
    "full_path": "Électronique → Téléphones → Smartphones"
  },
  "short_description": "Le meilleur smartphone de l'année",
  "description": "<p>Description HTML complète avec formatage...</p>",
  "price": "599.00",
  "compare_at_price": "799.00",
  "cost_price": "400.00",
  "final_price": "599.00",
  "discount_amount": "200.00",
  "has_discount": true,
  "stock_quantity": 45,
  "in_stock": true,
  "is_active": true,
  "images": [
    {
      "id": 1,
      "image": "http://api.com/media/products/galaxy-pro-1.jpg",
      "alt_text": "Vue de face",
      "is_primary": true,
      "order": 0
    },
    {
      "id": 2,
      "image": "http://api.com/media/products/galaxy-pro-2.jpg",
      "alt_text": "Vue de dos",
      "is_primary": false,
      "order": 1
    }
  ],
  "whatsapp_link": "https://wa.me/33612345678?text=Bonjour,%20je%20suis%20intéressé%20par%20Smartphone%20Galaxy%20Pro",
  "is_featured": true,
  "is_recommended": true,
  "featured_score": 85,
  "views_count": 1245,
  "clicks_count": 89,
  "meta_title": "Smartphone Galaxy Pro - Meilleur prix",
  "meta_description": "Achetez le Smartphone Galaxy Pro au meilleur prix...",
  "published_at": "2024-11-01T10:00:00Z",
  "created_at": "2024-10-28T15:30:00Z",
  "updated_at": "2024-11-20T09:15:00Z"
}
```

**Champs supplémentaires en mode détail:**

| Champ | Type | Description |
|-------|------|-------------|
| `description` | HTML | Description complète (peut contenir du HTML) |
| `images` | Array | Galerie d'images complète |
| `whatsapp_link` | URL | Lien WhatsApp pré-rempli pour contact |
| `featured_score` | Integer | Score de pertinence (0-100) |
| `views_count` | Integer | Nombre de consultations |
| `clicks_count` | Integer | Nombre de clics WhatsApp |
| `meta_title` | String | Titre SEO pour balise `<title>` |
| `meta_description` | String | Description SEO pour balise meta |

**Actions automatiques du backend:**

✅ **Compteur de vues:** Chaque consultation incrémente automatiquement `views_count`
✅ **Score recalculé:** Le score est automatiquement mis à jour quand le produit est modifié
✅ **Prix calculé:** `final_price` est toujours calculé avec la meilleure promotion active

**Exemple d'utilisation:**

```javascript
// Récupérer un produit par son slug
const getProductDetails = async (slug) => {
  const response = await fetch(`http://localhost:5000/api/v1/products/${slug}/`);
  const product = await response.json();
  
  // Afficher le prix avec ou sans promotion
  if (product.has_discount) {
    return `
      <div class="price">
        <span class="old-price">${product.compare_at_price}€</span>
        <span class="current-price">${product.final_price}€</span>
        <span class="savings">Économisez ${product.discount_amount}€</span>
      </div>
    `;
  }
  
  return `<div class="price">${product.final_price}€</div>`;
};
```

---

### 🔔 Incrémenter le clic WhatsApp

**Endpoint:** `POST /api/v1/products/{id}/track_whatsapp_click/`

**Usage:** Enregistrer un clic sur le bouton WhatsApp (important pour le scoring)

**Requête:** Vide

**Réponse:**
```json
{
  "status": "success",
  "clicks_count": 90
}
```

**Exemple d'utilisation:**

```javascript
// Enregistrer le clic avant de rediriger vers WhatsApp
const handleWhatsAppClick = async (productId) => {
  try {
    await fetch(`http://localhost:5000/api/v1/products/${productId}/track_whatsapp_click/`, {
      method: 'POST'
    });
    
    // Ensuite rediriger vers WhatsApp
    const product = await getProductDetails(productId);
    window.open(product.whatsapp_link, '_blank');
  } catch (error) {
    console.error('Erreur lors du tracking:', error);
  }
};
```

---

## CATÉGORIES

### 📁 Lister les catégories

**Endpoint:** `GET /api/v1/categories/`

**Usage:** Menu de navigation, filtres, arborescence

**Réponse:**
```json
{
  "count": 24,
  "results": [
    {
      "id": 1,
      "name": "Électronique",
      "slug": "electronique",
      "level": 0,
      "parent": null,
      "parent_name": null,
      "product_count": 156
    },
    {
      "id": 2,
      "name": "Téléphones",
      "slug": "telephones",
      "level": 1,
      "parent": 1,
      "parent_name": "Électronique",
      "product_count": 89
    }
  ]
}
```

**Champs:**

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Identifiant unique |
| `name` | String | Nom de la catégorie |
| `slug` | String | Pour les URLs |
| `level` | Integer | Niveau dans l'arborescence (0 = racine) |
| `parent` | Integer | ID de la catégorie parente (null si racine) |
| `product_count` | Integer | Nombre total de produits (incluant sous-catégories) |

**Filtres:**

```http
# Recherche par nom
GET /api/v1/categories/?search=électronique

# Catégories principales uniquement (sans parent)
GET /api/v1/categories/?is_main=true

# Catégories avec produits
GET /api/v1/categories/?has_products=true

# Par niveau
GET /api/v1/categories/?level=0

# Tri
GET /api/v1/categories/?ordering=name
GET /api/v1/categories/?ordering=-product_count  # Plus de produits en premier
```

---

### 📄 Détails d'une catégorie

**Endpoint:** `GET /api/v1/categories/{id}/` ou `GET /api/v1/categories/{slug}/`

**Réponse:**
```json
{
  "id": 5,
  "name": "Smartphones",
  "slug": "smartphones",
  "icon_file": "http://api.com/media/icons/smartphone.svg",
  "parent": {
    "id": 2,
    "name": "Téléphones",
    "slug": "telephones",
    "level": 1
  },
  "children": [
    {
      "id": 8,
      "name": "Smartphones Android",
      "slug": "smartphones-android",
      "level": 3
    },
    {
      "id": 9,
      "name": "Smartphones iOS",
      "slug": "smartphones-ios",
      "level": 3
    }
  ],
  "breadcrumb": [
    {"id": 1, "name": "Électronique", "slug": "electronique"},
    {"id": 2, "name": "Téléphones", "slug": "telephones"},
    {"id": 5, "name": "Smartphones", "slug": "smartphones"}
  ],
  "level": 2,
  "is_main_category": false,
  "product_count": 89,
  "direct_product_count": 45,
  "full_path": "Électronique → Téléphones → Smartphones",
  "created_at": "2024-10-15T08:00:00Z",
  "updated_at": "2024-11-18T14:20:00Z"
}
```

**Champs supplémentaires:**

| Champ | Type | Description |
|-------|------|-------------|
| `icon_file` | URL | Icône de la catégorie |
| `children` | Array | Sous-catégories directes |
| `breadcrumb` | Array | Fil d'Ariane complet |
| `full_path` | String | Chemin textuel complet |
| `direct_product_count` | Integer | Produits directement dans cette catégorie (sans enfants) |

**Exemple d'utilisation:**

```javascript
// Créer un fil d'Ariane
const renderBreadcrumb = (category) => {
  return category.breadcrumb.map(item => 
    `<a href="/categories/${item.slug}">${item.name}</a>`
  ).join(' → ');
};

// Créer un menu de navigation récursif
const renderCategoryMenu = async () => {
  const response = await fetch('http://localhost:5000/api/v1/categories/?is_main=true');
  const data = await response.json();
  
  return data.results.map(category => `
    <li>
      <a href="/categories/${category.slug}">
        ${category.name} (${category.product_count})
      </a>
    </li>
  `).join('');
};
```

---

### 🌳 Arborescence complète

**Endpoint:** `GET /api/v1/categories/tree/`

**Usage:** Afficher toute la hiérarchie de catégories (mega-menu, sidebar)

**Réponse:**
```json
[
  {
    "id": 1,
    "name": "Électronique",
    "slug": "electronique",
    "level": 0,
    "product_count": 245,
    "direct_product_count": 12,
    "children": [
      {
        "id": 2,
        "name": "Téléphones",
        "slug": "telephones",
        "level": 1,
        "product_count": 89,
        "direct_product_count": 5,
        "children": [
          {
            "id": 5,
            "name": "Smartphones",
            "slug": "smartphones",
            "level": 2,
            "product_count": 84,
            "direct_product_count": 84,
            "children": []
          }
        ]
      }
    ]
  }
]
```

**Exemple d'utilisation:**

```javascript
// Créer un mega-menu récursif
const renderMegaMenu = (categories) => {
  return categories.map(cat => `
    <div class="category-column">
      <h3>${cat.name}</h3>
      ${cat.children.length > 0 ? `
        <ul>
          ${cat.children.map(child => `
            <li>
              <a href="/categories/${child.slug}">
                ${child.name} <span>(${child.product_count})</span>
              </a>
            </li>
          `).join('')}
        </ul>
      ` : ''}
    </div>
  `).join('');
};
```

---

## PROMOTIONS

### 🎁 Lister les promotions actives

**Endpoint:** `GET /api/v1/promotions/`

**Usage:** Afficher les promotions en cours, bannières, badges

**Réponse:**
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "name": "Black Friday 2024",
      "slug": "black-friday-2024",
      "code": "BF2024",
      "promotion_type": "percentage",
      "value": "40.00",
      "active": true,
      "is_active_now": true,
      "start_at": "2024-11-24T00:00:00Z",
      "end_at": "2024-11-27T23:59:59Z",
      "is_stackable": false,
      "products_count": 156,
      "categories_count": 3,
      "applies_to_all": false
    }
  ]
}
```

**Types de promotions (`promotion_type`):**

| Type | Valeur | Description |
|------|--------|-------------|
| `fixed_price` | Prix final | Impose un prix fixe (ex: "49.99") |
| `fixed_amount` | Montant | Réduction en valeur (ex: "15.00" = -15€) |
| `percentage` | Pourcentage | Réduction en % (ex: "20.00" = -20%) |
| `buy_x_get_y` | N/A | Offre quantité (ex: Achetez 2, recevez 1) |

**Champs:**

| Champ | Type | Description |
|-------|------|-------------|
| `code` | String | Code promo (optionnel) |
| `is_active_now` | Boolean | Promotion en cours (entre start_at et end_at) |
| `is_stackable` | Boolean | Peut se cumuler avec d'autres |
| `applies_to_all` | Boolean | S'applique à tout le catalogue |

**Filtres:**

```http
# Promotions actives maintenant
GET /api/v1/promotions/?is_active_now=true

# Par type
GET /api/v1/promotions/?promotion_type=percentage

# Par code promo
GET /api/v1/promotions/?code=BF2024

# Promotions globales
GET /api/v1/promotions/?applies_to_all=true

# Tri
GET /api/v1/promotions/?ordering=-start_at  # Plus récentes
```

---

### 📄 Détails d'une promotion

**Endpoint:** `GET /api/v1/promotions/{id}/`

**Réponse:**
```json
{
  "id": 1,
  "name": "Black Friday 2024",
  "slug": "black-friday-2024",
  "code": "BF2024",
  "promotion_type": "percentage",
  "value": "40.00",
  "buy_x": null,
  "get_y": null,
  "active": true,
  "is_active_now": true,
  "start_at": "2024-11-24T00:00:00Z",
  "end_at": "2024-11-27T23:59:59Z",
  "is_stackable": false,
  "applies_to_all": false,
  "products": [
    {
      "id": 1,
      "name": "Smartphone Galaxy Pro",
      "slug": "smartphone-galaxy-pro",
      "price": "599.00",
      "main_image": "http://api.com/media/products/galaxy.jpg"
    }
  ],
  "categories": [
    {
      "id": 5,
      "name": "Smartphones",
      "slug": "smartphones",
      "level": 2,
      "full_path": "Électronique → Téléphones → Smartphones"
    }
  ],
  "usage_limit": 1000,
  "per_user_limit": 1,
  "usage_count": 245,
  "created_at": "2024-11-01T10:00:00Z",
  "updated_at": "2024-11-20T15:30:00Z"
}
```

**Exemple d'utilisation:**

```javascript
// Afficher les promotions actives sur la page d'accueil
const displayActivePromotions = async () => {
  const response = await fetch(
    'http://localhost:5000/api/v1/promotions/?is_active_now=true&ordering=-value'
  );
  const data = await response.json();
  
  return data.results.map(promo => {
    let badge = '';
    if (promo.promotion_type === 'percentage') {
      badge = `-${promo.value}%`;
    } else if (promo.promotion_type === 'fixed_amount') {
      badge = `-${promo.value}€`;
    }
    
    return `
      <div class="promo-banner">
        <h3>${promo.name}</h3>
        <span class="badge">${badge}</span>
        <p>Jusqu'au ${new Date(promo.end_at).toLocaleDateString()}</p>
      </div>
    `;
  }).join('');
};
```

**💡 Règle importante:**

Le backend calcule automatiquement le meilleur prix pour chaque produit:
- Si plusieurs promotions s'appliquent, il choisit la plus avantageuse
- Le `final_price` du produit est toujours le prix après meilleure promo
- Vous n'avez PAS besoin de calculer les prix vous-même!

---

## NEWSLETTER

### ✉️ Inscription à la newsletter

**Endpoint:** `POST /api/v1/newsletter/subscribers/`

**Usage:** Formulaire d'inscription newsletter

**Requête:**
```json
{
  "email": "marie@example.com",
  "name": "Marie Dupont",
  "source": "homepage"
}
```

**Champs:**

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `email` | String | ✅ Oui | Email valide |
| `name` | String | ❌ Non | Nom de l'abonné |
| `source` | String | ❌ Non | Source d'inscription (pour tracking) |

**Réponse (succès):**
```json
{
  "id": 123,
  "email": "marie@example.com",
  "name": "Marie Dupont",
  "confirmed": false,
  "subscribed": true,
  "source": "homepage",
  "tags": [],
  "created_at": "2024-11-22T14:30:00Z"
}
```

**Comportement automatique du backend:**

✅ **Email de confirmation envoyé automatiquement** avec lien unique
✅ **Token de confirmation généré** automatiquement
✅ **Validation d'email** (format, doublons)

**Réponse (erreur - email déjà inscrit):**
```json
{
  "email": ["Un abonné avec cet email existe déjà."]
}
```

**Exemple d'utilisation:**

```javascript
// Formulaire d'inscription
const subscribeToNewsletter = async (email, name) => {
  try {
    const response = await fetch('http://localhost:5000/api/v1/newsletter/subscribers/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: email,
        name: name,
        source: 'footer'
      })
    });
    
    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        message: 'Un email de confirmation vous a été envoyé !'
      };
    } else {
      const error = await response.json();
      return {
        success: false,
        message: error.email ? error.email[0] : 'Erreur lors de l\'inscription'
      };
    }
  } catch (error) {
    return {
      success: false,
      message: 'Erreur de connexion au serveur'
    };
  }
};
```

---

### ✅ Confirmer l'inscription

**Endpoint:** `POST /api/v1/newsletter/subscribers/{id}/confirm/`

**Usage:** Valider l'email après clic sur le lien de confirmation

**Requête:**
```json
{
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Réponse (succès):**
```json
{
  "status": "confirmed",
  "message": "Votre inscription à la newsletter est confirmée !"
}
```

**Réponse (déjà confirmé):**
```json
{
  "status": "already_confirmed",
  "message": "Vous êtes déjà abonné à la newsletter."
}
```

**Réponse (token invalide):**
```json
{
  "error": "Token de confirmation invalide"
}
```

**Exemple d'utilisation:**

```javascript
// Page de confirmation (/confirm?token=xxx&subscriber=123)
const confirmSubscription = async (subscriberId, token) => {
  const response = await fetch(
    `http://localhost:5000/api/v1/newsletter/subscribers/${subscriberId}/confirm/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token })
    }
  );
  
  const data = await response.json();
  
  if (data.status === 'confirmed') {
    showMessage('✅ Votre inscription est confirmée !', 'success');
  } else if (data.status === 'already_confirmed') {
    showMessage('ℹ️ Vous êtes déjà abonné.', 'info');
  } else {
    showMessage('❌ Lien invalide ou expiré.', 'error');
  }
};
```

---

### 🔕 Désabonnement

**Endpoint:** `POST /api/v1/newsletter/subscribers/{id}/unsubscribe/`

**Usage:** Se désabonner de la newsletter

**Requête:**
```json
{
  "token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Réponse:**
```json
{
  "status": "unsubscribed",
  "message": "Vous avez été désabonné de la newsletter."
}
```

**Exemple d'utilisation:**

```javascript
// Lien dans l'email: /unsubscribe?token=xxx&subscriber=123
const unsubscribeFromNewsletter = async (subscriberId, token) => {
  const response = await fetch(
    `http://localhost:5000/api/v1/newsletter/subscribers/${subscriberId}/unsubscribe/`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ token })
    }
  );
  
  const data = await response.json();
  showMessage(data.message, data.status === 'unsubscribed' ? 'success' : 'error');
};
```

---

## SERVICES ET PARAMÈTRES

### 🛠️ Services institutionnels

**Endpoint:** `GET /api/v1/services/`

**Usage:** Afficher les services proposés (livraison, SAV, garanties...)

**Réponse:**
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "title": "Livraison gratuite dès 50€",
      "slug": "livraison-gratuite",
      "description": "Profitez de la livraison gratuite sur toutes vos commandes de plus de 50€",
      "image": "http://api.com/media/services/delivery.svg",
      "order": 1,
      "is_active": true,
      "external_link": null
    },
    {
      "id": 2,
      "title": "SAV réactif",
      "slug": "sav-reactif",
      "description": "Notre service client répond sous 48h",
      "image": "http://api.com/media/services/support.svg",
      "order": 2,
      "is_active": true,
      "external_link": "https://support.example.com"
    }
  ]
}
```

**Filtres:**

```http
# Uniquement les services actifs
GET /api/v1/services/?is_active=true

# Tri par ordre
GET /api/v1/services/?ordering=order
```

---

### ⚙️ Paramètres du site

**Endpoint:** `GET /api/v1/settings/`

**Usage:** Récupérer les informations globales du site (coordonnées, réseaux sociaux, etc.)

**Réponse:**
```json
{
  "whatsapp_number": "+33612345678",
  "contact_email": "contact@example.com",
  "contact_phone": "+33123456789",
  "contact_address": "123 Rue Example, 75001 Paris",
  "company_name": "Ma Boutique",
  "company_description": "Votre spécialiste en électronique",
  "social_links": {
    "facebook": "https://facebook.com/maboutique",
    "instagram": "https://instagram.com/maboutique",
    "twitter": "https://twitter.com/maboutique",
    "linkedin": null
  },
  "updated_at": "2024-11-15T10:00:00Z"
}
```

**Exemple d'utilisation:**

```javascript
// Charger les paramètres globaux au démarrage de l'app
const loadSiteSettings = async () => {
  const response = await fetch('http://localhost:5000/api/v1/settings/');
  const settings = await response.json();
  
  // Mettre à jour le footer
  document.getElementById('contact-email').textContent = settings.contact_email;
  document.getElementById('contact-phone').textContent = settings.contact_phone;
  
  // Créer les liens réseaux sociaux
  const socials = Object.entries(settings.social_links)
    .filter(([_, url]) => url)
    .map(([platform, url]) => `
      <a href="${url}" target="_blank" rel="noopener">
        <i class="icon-${platform}"></i>
      </a>
    `).join('');
  
  document.getElementById('social-links').innerHTML = socials;
};
```

---

### 🔗 Liens réseaux sociaux

**Endpoint:** `GET /api/v1/social-links/`

**Usage:** Récupérer les liens vers les réseaux sociaux

**Réponse:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Facebook",
      "url": "https://facebook.com/maboutique"
    },
    {
      "id": 2,
      "name": "Instagram",
      "url": "https://instagram.com/maboutique"
    },
    {
      "id": 3,
      "name": "Twitter",
      "url": "https://twitter.com/maboutique"
    }
  ]
}
```

---

## FILTRES ET RECHERCHE

### 🔍 Recherche Globale

**Fonctionnement:**

La recherche textuelle (`?search=`) fonctionne sur:
- **Produits:** nom, marque, description, SKU, code-barres
- **Catégories:** nom, slug
- **Promotions:** nom, code

**Exemples:**

```http
# Recherche de produits
GET /api/v1/products/?search=samsung galaxy

# Recherche de catégories
GET /api/v1/categories/?search=téléphone

# Recherche de promotions
GET /api/v1/promotions/?search=black friday
```

---

### 🎯 Filtres Avancés

**Combinaison de filtres:**

Vous pouvez combiner plusieurs filtres dans une seule requête:

```http
# Smartphones Samsung entre 300€ et 800€ en stock avec promotion
GET /api/v1/products/?category_slug=smartphones&brand=Samsung&min_price=300&max_price=800&in_stock=true&has_discount=true&ordering=-featured_score
```

**Filtres par date:**

```http
# Produits ajoutés ce mois
GET /api/v1/products/?created_after=2024-11-01

# Promotions se terminant avant le 31/12
GET /api/v1/promotions/?end_before=2024-12-31T23:59:59Z
```

---

### 📊 Tri des résultats

**Paramètre:** `?ordering=`

**Valeurs possibles:**

| Tri | Ordre croissant | Ordre décroissant |
|-----|-----------------|-------------------|
| Nom | `ordering=name` | `ordering=-name` |
| Prix | `ordering=price` | `ordering=-price` |
| Date création | `ordering=created_at` | `ordering=-created_at` |
| Vues | `ordering=views_count` | `ordering=-views_count` |
| Score | `ordering=featured_score` | `ordering=-featured_score` |

**Exemples:**

```http
# Produits les moins chers
GET /api/v1/products/?ordering=price

# Produits les plus récents
GET /api/v1/products/?ordering=-created_at

# Produits les plus consultés
GET /api/v1/products/?ordering=-views_count

# Meilleur score en premier
GET /api/v1/products/?ordering=-featured_score
```

---

## GESTION DES ERREURS

### Codes HTTP

| Code | Signification | Action |
|------|---------------|--------|
| 200 | OK | Succès |
| 201 | Created | Ressource créée avec succès |
| 400 | Bad Request | Données invalides (vérifier le format) |
| 401 | Unauthorized | Token manquant ou invalide |
| 403 | Forbidden | Pas les droits nécessaires |
| 404 | Not Found | Ressource introuvable |
| 500 | Server Error | Erreur serveur (contacter l'admin) |

### Format des erreurs

**Erreur de validation:**
```json
{
  "email": ["Saisissez une adresse e-mail valide."],
  "name": ["Ce champ ne peut pas être vide."]
}
```

**Erreur générale:**
```json
{
  "detail": "Les informations d'authentification n'ont pas été fournies."
}
```

### Gestion frontend

```javascript
// Exemple de gestion d'erreur robuste
const fetchProducts = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/v1/products/');
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Aucun produit trouvé');
      } else if (response.status === 500) {
        throw new Error('Erreur serveur, veuillez réessayer plus tard');
      } else {
        throw new Error('Erreur lors du chargement des produits');
      }
    }
    
    const data = await response.json();
    return data.results;
    
  } catch (error) {
    console.error('Erreur:', error);
    showErrorMessage(error.message);
    return [];
  }
};
```

---

## CHECKLIST DÉVELOPPEMENT

### 📋 Phase 1 - Configuration initiale

- [ ] Configurer l'URL de base de l'API (dev/prod)
- [ ] Tester la connexion à l'API (`GET /api/v1/products/`)
- [ ] Vérifier que les CORS sont configurés (sinon demander au backend)
- [ ] Créer un service/module centralisé pour les appels API

### 📋 Phase 2 - Page d'accueil

**Produits "À la une":**
- [ ] Récupérer les produits featured (`?is_featured=true&ordering=-featured_score`)
- [ ] Afficher les badges "À la une"
- [ ] Implémenter le carrousel/slider de produits

**Produits recommandés:**
- [ ] Récupérer les produits recommandés (`?is_recommended=true`)
- [ ] Créer une section "Nos recommandations"

**Promotions actives:**
- [ ] Récupérer les promotions en cours (`?is_active_now=true`)
- [ ] Afficher les bannières de promotion
- [ ] Afficher les comptes à rebours (end_at)

**Services:**
- [ ] Récupérer les services actifs (`?is_active=true&ordering=order`)
- [ ] Afficher les icônes et descriptions

### 📋 Phase 3 - Catalogue produits

**Liste de produits:**
- [ ] Implémenter la pagination (next/previous)
- [ ] Afficher les filtres (catégories, prix, stock, promotions)
- [ ] Implémenter la recherche textuelle
- [ ] Implémenter le tri (prix, date, popularité)
- [ ] Afficher les badges (featured, recommended, promo)
- [ ] Afficher les prix barrés si `has_discount=true`

**Fiche produit:**
- [ ] Récupérer les détails par slug ou ID
- [ ] Afficher la galerie d'images (image principale + secondaires)
- [ ] Afficher le prix final (avec ou sans promo)
- [ ] Afficher la disponibilité (in_stock)
- [ ] Implémenter le bouton WhatsApp avec tracking
- [ ] Afficher le fil d'Ariane (breadcrumb de la catégorie)
- [ ] Ajouter les meta tags SEO (meta_title, meta_description)

### 📋 Phase 4 - Navigation

**Menu catégories:**
- [ ] Récupérer l'arborescence complète (`/categories/tree/`)
- [ ] Créer un menu récursif (catégories → sous-catégories)
- [ ] Implémenter les liens vers les pages catégories
- [ ] Afficher le nombre de produits par catégorie

**Fil d'Ariane:**
- [ ] Utiliser le champ `breadcrumb` des catégories
- [ ] Créer des liens cliquables pour chaque niveau

### 📋 Phase 5 - Newsletter

**Formulaire d'inscription:**
- [ ] Créer le formulaire (email + nom optionnel)
- [ ] Valider l'email côté frontend
- [ ] Envoyer la requête POST à `/newsletter/subscribers/`
- [ ] Afficher un message de confirmation
- [ ] Gérer les erreurs (email déjà inscrit, format invalide)

**Page de confirmation:**
- [ ] Créer la route `/confirm?token=xxx&subscriber=123`
- [ ] Appeler l'endpoint de confirmation
- [ ] Afficher un message de succès ou d'erreur

**Page de désabonnement:**
- [ ] Créer la route `/unsubscribe?token=xxx&subscriber=123`
- [ ] Appeler l'endpoint de désabonnement
- [ ] Afficher un message de confirmation

### 📋 Phase 6 - Footer & Informations

**Paramètres du site:**
- [ ] Charger les paramètres au démarrage (`/settings/`)
- [ ] Afficher les coordonnées de contact
- [ ] Créer les liens WhatsApp/email
- [ ] Afficher les réseaux sociaux

**Services:**
- [ ] Afficher les services en footer
- [ ] Créer les liens externes si présents

### 📋 Phase 7 - Optimisations

**Performance:**
- [ ] Implémenter un cache local pour les catégories (rarement modifiées)
- [ ] Implémenter un cache pour les paramètres du site
- [ ] Lazy loading des images produits
- [ ] Pagination infinie ou classique selon UX

**SEO:**
- [ ] Utiliser les slugs dans les URLs
- [ ] Ajouter les meta tags depuis les données API
- [ ] Implémenter le sitemap.xml (généré côté backend)
- [ ] Ajouter les données structurées (schema.org)

**UX:**
- [ ] Loading states pendant les requêtes
- [ ] Messages d'erreur clairs et traduits
- [ ] Feedback visuel sur les actions (ajout panier, inscription newsletter)
- [ ] États vides (pas de produits, pas de résultats de recherche)

### 📋 Phase 8 - Tests

**Tests fonctionnels:**
- [ ] Tester la navigation entre catégories
- [ ] Tester la recherche de produits
- [ ] Tester les filtres et le tri
- [ ] Tester l'inscription newsletter (avec vrai email)
- [ ] Tester le tracking WhatsApp

**Tests edge cases:**
- [ ] Produits sans image
- [ ] Catégories vides
- [ ] Promotions expirées
- [ ] API hors ligne (afficher un message)

---

## 💡 BONNES PRATIQUES

### 1. Ne calculez JAMAIS les prix vous-même

❌ **Mauvais:**
```javascript
// N'essayez pas de calculer les promotions
const finalPrice = product.price * (1 - promotion.value / 100);
```

✅ **Bon:**
```javascript
// Utilisez toujours le prix calculé par le backend
const finalPrice = product.final_price;
```

**Pourquoi?** Le backend gère automatiquement:
- Les promotions multiples (il choisit la meilleure)
- Les promotions sur catégories parentes
- Les dates de validité
- Les limites d'utilisation

---

### 2. Utilisez les slugs pour les URLs

✅ **Bon:**
```javascript
// URLs SEO-friendly
/produits/smartphone-galaxy-pro
/categories/electronique
/promotions/black-friday-2024
```

❌ **Mauvais:**
```javascript
// URLs avec IDs seulement
/produits/123
/categories/5
```

---

### 3. Affichez toujours les badges automatiques

Le backend calcule automatiquement:
- `is_featured` - Badge "À la une" (score ≥ 70)
- `is_recommended` - Badge "Recommandé" (score ≥ 50)
- `has_discount` - Badge "Promotion"

```javascript
// Afficher les badges pertinents
const renderProductBadges = (product) => {
  const badges = [];
  
  if (product.is_featured) {
    badges.push('<span class="badge badge-featured">⭐ À la une</span>');
  }
  if (product.is_recommended) {
    badges.push('<span class="badge badge-recommended">👍 Recommandé</span>');
  }
  if (product.has_discount) {
    const discount = ((product.compare_at_price - product.final_price) / product.compare_at_price * 100).toFixed(0);
    badges.push(`<span class="badge badge-promo">-${discount}%</span>`);
  }
  if (!product.in_stock) {
    badges.push('<span class="badge badge-stock">Rupture</span>');
  }
  
  return badges.join('');
};
```

---

### 4. Trackez les interactions importantes

Pour améliorer le système de recommandation:

```javascript
// Tracker le clic WhatsApp
const handleWhatsAppClick = async (productId, whatsappLink) => {
  // 1. Enregistrer le clic (important pour le scoring!)
  await fetch(`/api/v1/products/${productId}/track_whatsapp_click/`, {
    method: 'POST'
  });
  
  // 2. Ouvrir WhatsApp
  window.open(whatsappLink, '_blank');
};
```

**Note:** Le compteur de vues est automatiquement incrémenté à chaque consultation de fiche produit.

---

### 5. Gérez proprement les états de chargement

```javascript
// Exemple complet avec loading et erreurs
const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/api/v1/products/?is_featured=true');
        
        if (!response.ok) {
          throw new Error('Erreur lors du chargement');
        }
        
        const data = await response.json();
        setProducts(data.results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, []);
  
  if (loading) return <Loader />;
  if (error) return <ErrorMessage message={error} />;
  if (products.length === 0) return <EmptyState message="Aucun produit trouvé" />;
  
  return <ProductGrid products={products} />;
};
```

---

### 6. Utilisez la pagination intelligemment

```javascript
// Pagination classique
const loadPage = async (page) => {
  const response = await fetch(`/api/v1/products/?page=${page}&page_size=20`);
  const data = await response.json();
  
  return {
    products: data.results,
    hasNext: data.next !== null,
    hasPrevious: data.previous !== null,
    totalCount: data.count
  };
};

// Ou infinite scroll
const loadMoreProducts = async (nextUrl) => {
  if (!nextUrl) return;
  
  const response = await fetch(nextUrl);
  const data = await response.json();
  
  setProducts(prev => [...prev, ...data.results]);
  setNextUrl(data.next);
};
```

---

### 7. Centralisez vos appels API

```javascript
// api.js - Service centralisé
const API_BASE = 'http://localhost:5000/api/v1';

export const api = {
  // Produits
  getProducts: (params = {}) => 
    fetch(`${API_BASE}/products/?${new URLSearchParams(params)}`).then(r => r.json()),
  
  getProduct: (slug) => 
    fetch(`${API_BASE}/products/${slug}/`).then(r => r.json()),
  
  trackWhatsAppClick: (productId) => 
    fetch(`${API_BASE}/products/${productId}/track_whatsapp_click/`, { method: 'POST' }),
  
  // Catégories
  getCategories: () => 
    fetch(`${API_BASE}/categories/`).then(r => r.json()),
  
  getCategoryTree: () => 
    fetch(`${API_BASE}/categories/tree/`).then(r => r.json()),
  
  // Newsletter
  subscribe: (email, name) => 
    fetch(`${API_BASE}/newsletter/subscribers/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, name })
    }).then(r => r.json()),
  
  // Paramètres
  getSettings: () => 
    fetch(`${API_BASE}/settings/`).then(r => r.json()),
  
  getServices: () => 
    fetch(`${API_BASE}/services/?is_active=true&ordering=order`).then(r => r.json())
};

// Utilisation
const products = await api.getProducts({ is_featured: true, ordering: '-featured_score' });
```

---

## 🎬 EXEMPLES COMPLETS

### Exemple 1: Page d'accueil complète

```javascript
import { api } from './api';

const HomePage = () => {
  const [featured, setFeatured] = useState([]);
  const [recommended, setRecommended] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadHomeData = async () => {
      try {
        const [featuredData, recommendedData, promosData, servicesData] = await Promise.all([
          api.getProducts({ is_featured: true, ordering: '-featured_score', page_size: 8 }),
          api.getProducts({ is_recommended: true, ordering: '-featured_score', page_size: 12 }),
          fetch('/api/v1/promotions/?is_active_now=true').then(r => r.json()),
          api.getServices()
        ]);
        
        setFeatured(featuredData.results);
        setRecommended(recommendedData.results);
        setPromotions(promosData.results);
        setServices(servicesData.results);
      } catch (error) {
        console.error('Erreur chargement page d\'accueil:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadHomeData();
  }, []);
  
  if (loading) return <Loader />;
  
  return (
    <div>
      <Hero />
      <PromotionBanner promotions={promotions} />
      <FeaturedProducts products={featured} />
      <RecommendedProducts products={recommended} />
      <ServicesSection services={services} />
    </div>
  );
};
```

---

### Exemple 2: Page catalogue avec filtres

```javascript
const CatalogPage = () => {
  const [products, setProducts] = useState([]);
  const [filters, setFilters] = useState({
    search: '',
    category_slug: '',
    min_price: '',
    max_price: '',
    in_stock: true,
    has_discount: false,
    ordering: '-created_at'
  });
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  useEffect(() => {
    const loadProducts = async () => {
      const params = { ...filters, page, page_size: 20 };
      
      // Nettoyer les filtres vides
      Object.keys(params).forEach(key => 
        (params[key] === '' || params[key] === null) && delete params[key]
      );
      
      const data = await api.getProducts(params);
      setProducts(data.results);
      setTotalCount(data.count);
    };
    
    loadProducts();
  }, [filters, page]);
  
  const updateFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset à la page 1
  };
  
  return (
    <div className="catalog">
      <aside className="filters">
        <input 
          type="search" 
          placeholder="Rechercher..."
          value={filters.search}
          onChange={e => updateFilter('search', e.target.value)}
        />
        
        <PriceRangeFilter 
          min={filters.min_price}
          max={filters.max_price}
          onChange={(min, max) => {
            setFilters(prev => ({ ...prev, min_price: min, max_price: max }));
          }}
        />
        
        <label>
          <input 
            type="checkbox"
            checked={filters.in_stock}
            onChange={e => updateFilter('in_stock', e.target.checked)}
          />
          En stock uniquement
        </label>
        
        <label>
          <input 
            type="checkbox"
            checked={filters.has_discount}
            onChange={e => updateFilter('has_discount', e.target.checked)}
          />
          En promotion
        </label>
        
        <select 
          value={filters.ordering}
          onChange={e => updateFilter('ordering', e.target.value)}
        >
          <option value="-created_at">Plus récents</option>
          <option value="price">Prix croissant</option>
          <option value="-price">Prix décroissant</option>
          <option value="-featured_score">Meilleurs scores</option>
        </select>
      </aside>
      
      <main className="products">
        <div className="results-info">
          {totalCount} produit(s) trouvé(s)
        </div>
        
        <ProductGrid products={products} />
        
        <Pagination 
          currentPage={page}
          totalItems={totalCount}
          itemsPerPage={20}
          onPageChange={setPage}
        />
      </main>
    </div>
  );
};
```

---

### Exemple 3: Fiche produit complète

```javascript
const ProductPage = ({ slug }) => {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadProduct = async () => {
      try {
        const data = await api.getProduct(slug);
        setProduct(data);
        
        // Mise à jour des meta tags SEO
        document.title = data.meta_title || data.name;
        document.querySelector('meta[name="description"]').content = 
          data.meta_description || data.short_description;
      } catch (error) {
        console.error('Produit introuvable:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadProduct();
  }, [slug]);
  
  const handleWhatsAppClick = async () => {
    await api.trackWhatsAppClick(product.id);
    window.open(product.whatsapp_link, '_blank');
  };
  
  if (loading) return <Loader />;
  if (!product) return <NotFound />;
  
  return (
    <div className="product-page">
      <Breadcrumb items={product.category.breadcrumb} />
      
      <div className="product-content">
        <ImageGallery images={product.images} />
        
        <div className="product-info">
          <h1>{product.name}</h1>
          
          <div className="badges">
            {product.is_featured && <span className="badge-featured">⭐ À la une</span>}
            {product.is_recommended && <span className="badge-recommended">👍 Recommandé</span>}
          </div>
          
          <div className="price">
            {product.has_discount ? (
              <>
                <span className="old-price">{product.compare_at_price}€</span>
                <span className="current-price">{product.final_price}€</span>
                <span className="savings">Économisez {product.discount_amount}€</span>
              </>
            ) : (
              <span className="current-price">{product.final_price}€</span>
            )}
          </div>
          
          <div className="stock">
            {product.in_stock ? (
              <span className="in-stock">✓ En stock</span>
            ) : (
              <span className="out-of-stock">✗ Rupture de stock</span>
            )}
          </div>
          
          <div className="description">
            <h2>Description</h2>
            <div dangerouslySetInnerHTML={{ __html: product.description }} />
          </div>
          
          <button 
            className="btn-whatsapp"
            onClick={handleWhatsAppClick}
            disabled={!product.in_stock}
          >
            <i className="icon-whatsapp"></i>
            Commander sur WhatsApp
          </button>
          
          <div className="stats">
            <span>{product.views_count} consultations</span>
            <span>{product.clicks_count} demandes</span>
          </div>
        </div>
      </div>
    </div>
  );
};
```

---

## 🚀 DÉMARRAGE RAPIDE

### Installation minimale

```bash
# 1. Installer les dépendances (exemple React)
npm install

# 2. Configurer l'URL de l'API
# Dans .env
REACT_APP_API_URL=http://localhost:5000/api/v1

# 3. Lancer le projet
npm start
```

### Premiers tests

```javascript
// Test de connexion à l'API
fetch('http://localhost:5000/api/v1/products/')
  .then(r => r.json())
  .then(data => console.log('Produits:', data.results))
  .catch(err => console.error('Erreur:', err));
```

---

## 📞 SUPPORT

### En cas de problème

1. **Vérifier les CORS:** Si vous avez des erreurs de CORS, contactez l'équipe backend
2. **Vérifier les URLs:** Assurez-vous d'utiliser la bonne URL de base (dev/prod)
3. **Consulter la doc Swagger:** Disponible à `/swagger/` ou `/redoc/`
4. **Logs backend:** En cas d'erreur 500, demander les logs au backend

### Documentation technique complète

- **Swagger UI:** http://localhost:5000/swagger/
- **ReDoc:** http://localhost:5000/redoc/
- **Admin Django:** http://localhost:5000/admin/

---

**Dernière mise à jour:** 22 novembre 2024
**Version API:** v1.0
**Contact:** dev-backend@example.com
