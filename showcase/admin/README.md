# Django Admin - Architecture Documentation

Une interface administrateur professionnelle, modulaire et scalable pour la gestion complète des produits, promotions, newsletters et paramètres du site.

## 📁 Structure Modulaire

```
admin/
├── __init__.py                    # Imports et configuration globale
├── base.py                        # Classes de base réutilisables
├── utils.py                       # Utilitaires HTML et helpers
├── filters.py                     # Filtres personnalisés
├── displays.py                    # Méthodes de rendu pour l'affichage
├── actions.py                     # Actions en masse pour admin
├── category_admin.py              # Admin pour les catégories
├── product_admin.py               # Admin pour les produits
├── promotion_admin.py             # Admin pour les promotions
├── newsletter_admin.py            # Admin pour les newsletters
├── settings_admin.py              # Admin pour les paramètres
└── README.md                      # Cette documentation
```

## 🎯 Principes Architecturaux

### 1. **Séparation des Responsabilités**
- **base.py**: Classes de base génériques (mixins, optimisations)
- **utils.py**: Utilitaires HTML et helpers réutilisables
- **filters.py**: Filtres personnalisés et logique de filtrage
- **displays.py**: Méthodes de rendu et formatage
- **actions.py**: Actions en masse et opérations en masse
- **[model]_admin.py**: Logique spécifique au modèle

### 2. **Réutilisabilité**
- Classes de base extensibles
- Utilitaires génériques et réutilisables
- Patterns DRY appliqués partout
- Aucune duplication de code

### 3. **Performance**
- QuerySets optimisés avec `select_related` et `prefetch_related`
- Pas de requête N+1
- Pagination automatique Django
- Caching dans les affichages

### 4. **Maintenabilité**
- Responsabilités claires
- Code organisé et trouvable
- Documentation complète
- Facile à étendre

## 📦 Modules

### `base.py` - Classes de Base

```python
# Classes de base avec optimisations intégrées
OptimizedModelAdmin          # ModelAdmin avec support des optimisations
OptimizedTabularInline      # TabularInline avec support des optimisations
TimestampReadOnlyMixin      # Ajoute created_at, updated_at comme read-only
UserTrackingMixin           # Track user qui modifie les objets
SingletonAdminMixin         # Pour modèles singleton (une seule instance)
```

#### Utilisation

```python
@admin.register(MyModel)
class MyModelAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):
    # ...

    def optimize_queryset(self, qs):
        """Override pour optimiser"""
        return qs.select_related('related')
```

### `utils.py` - Utilitaires HTML

Classe `AdminDisplay` pour rendu HTML simplifié:

```python
from admin.utils import AdminDisplay

# Images
AdminDisplay.image_thumbnail(url, alt_text, width, height)

# Badges
AdminDisplay.badge(text, bg_color, text_color, size)
AdminDisplay.status_badge(status, status_map)

# Boîtes d'info
AdminDisplay.info_box(title, content, bg_color)

# Galeries
AdminDisplay.gallery(images, max_width, max_height)

# Alertes
AdminDisplay.alert(message, level)  # level: info, success, warning, error

# Boutons et liens
AdminDisplay.button(text, href, style)
AdminDisplay.link(text, href, icon)
```

### `filters.py` - Filtres Personnalisés

Filtres simples et avancés:

- `StockStatusFilter`: En stock / Stock faible / Rupture
- `PriceRangeFilter`: Gammes de prix prédéfinies
- `DiscountFilter`: Produits avec/sans réduction
- `NewProductFilter`: Produits récents (7j/30j/90j)
- `EngagementFilter`: Par niveau d'engagement (vues, clics)
- `CategoryLevelFilter`: Par profondeur de catégorie

#### Utilisation

```python
class ProductAdmin(OptimizedModelAdmin):
    list_filter = [
        'is_active',
        StockStatusFilter,      # Filtre personnalisé
        PriceRangeFilter,
        NewProductFilter,
        # ...
    ]
```

### `displays.py` - Méthodes de Rendu

Classes groupant méthodes de rendu par modèle:

#### `ProductDisplays`
- `thumbnail()`: Miniature produit
- `main_image_preview()`: Aperçu image principale
- `gallery_preview()`: Galerie des images
- `formatted_price()`: Prix avec réduction
- `stock_status()`: Indicateur stock
- `featured_badge()`: Badge vedette avec score
- `recommended_badge()`: Badge recommandé
- `stats_display()`: Statistiques d'engagement
- `whatsapp_link_display()`: Lien WhatsApp
- `algorithm_info()`: Détails des algorithmes

#### `CategoryDisplays`
- `icon_preview()`: Aperçu icône
- `product_count_display()`: Compte récursif
- `direct_product_count_display()`: Compte direct

#### `ImageDisplays`
- `thumbnail()`: Miniature image

#### Utilisation

```python
class ProductAdmin(OptimizedModelAdmin):
    list_display = [
        'product_thumbnail',
        'name',
        'formatted_price',
        'featured_badge',
        'stats_display',
    ]

    def product_thumbnail(self, obj):
        return ProductDisplays.thumbnail(obj)
```

### `actions.py` - Actions en Masse

#### `ProductActions`
- `recalculate_scores()`: Recalculer featured/recommended
- `force_featured()`: Forcer en vedette
- `force_recommended()`: Forcer en recommandé
- `exclude_from_featured()`: Exclure des vedettes
- `exclude_from_recommended()`: Exclure des recommandés
- `activate()`: Activer produits
- `deactivate()`: Désactiver produits
- `mark_in_stock()`: Marquer en stock
- `mark_out_of_stock()`: Marquer rupture

#### `CategoryActions`
- `rebuild_tree()`: Reconstruire arbre MPPT

#### `PromotionActions`
- `activate_promotions()`: Activer promotions
- `deactivate_promotions()`: Désactiver promotions
- `mark_stackable()`: Marquer empilables
- `mark_non_stackable()`: Marquer non-empilables

#### `NewsletterActions`
- `mark_confirmed()`: Marquer confirmés
- `mark_unconfirmed()`: Marquer non-confirmés
- `unsubscribe_users()`: Désabonner
- `subscribe_users()`: Réabonner

#### Utilisation

```python
class ProductAdmin(OptimizedModelAdmin):
    actions = [
        ('recalculate_scores', ProductActions.recalculate_scores),
        ('force_featured', ProductActions.force_featured),
    ]

    def recalculate_scores(self, request, queryset):
        return ProductActions.recalculate_scores(self, request, queryset)
    recalculate_scores.short_description = "🔄 Recalculer scores"
```

## 🎨 Admins Spécifiques

### CategoryAdmin

**Fonctionnalités:**
- Hiérarchie MPPT visuelle avec indentation
- Compte de produits récursif et direct
- Aperçu icône
- Reconstruction d'arbre en cas de corruption
- Édition rapide du slug

**Filtres:** Niveau, date création/modification

**Actions:** Reconstruire l'arbre MPPT

### ProductAdmin

**Fonctionnalités:**
- Miniatures produits dans la liste
- Multi-images inline
- Aperçu image principale et galerie
- Statistiques d'engagement (vues, clics)
- Scores des algorithmes avec explications
- Badges vedette/recommandé
- Lien WhatsApp de test
- Contrôles manuels (force/exclude)

**Filtres:**
- Stock (En stock / Faible / Rupture)
- Prix (gammes)
- Réductions
- Nouveaux produits
- Engagement
- Catégorie, Marque
- Date de création

**Actions:**
- Recalculer scores
- Forcer/exclure vedettes/recommandés
- Activer/désactiver
- Marquer en stock/rupture

### PromotionAdmin

**Fonctionnalités:**
- Vue d'ensemble des promotions actives/programmées
- Historique d'utilisation inline
- Détails de configuration (produits, catégories)
- Limite d'utilisation avec progression
- Statut d'empilement

**Filtres:**
- Active/Inactive
- Type de promotion
- Empilable/Non-empilable
- Dates de programmation

**Actions:**
- Activer/désactiver
- Marquer empilable/non-empilable

### NewsletterAdmin

Comporte **4 modèles** avec admins distincts:

#### NewsletterSubscriber
- Liste d'abonnés avec statut confirmation/abonnement
- Métadonnées (source, tags, IP)
- Actions de confirmation/désabonnement

#### NewsletterTemplate
- Gestion des modèles HTML/Texte
- Configuration par défaut
- Compteur de campagnes

#### NewsletterCampaign
- Programmation des campagnes
- Sélection des destinataires
- Historique d'envoi (logs inline)
- Statut en temps réel

#### NewsletterLog
- Historique d'envoi par destinataire
- Logs d'erreurs
- Recherche et filtrage

### SettingsAdmin

**Models:**

#### SiteSettings (Singleton)
- Infos de contact (WhatsApp, téléphone, email, adresse)
- Infos entreprise
- Réseaux sociaux

#### SocialLink
- Gestion des liens réseaux sociaux

#### Service
- Services affichés sur page services
- Ordre d'affichage
- Statut actif/inactif

## 🔧 Patterns Courants

### Ajouter un Nouveau Filtre

```python
# admin/filters.py
class MyFilter(SimpleListFilter):
    title = _("Mon filtre")
    parameter_name = "my_filter"

    def lookups(self, request, model_admin):
        return (
            ("value1", _("Libellé 1")),
            ("value2", _("Libellé 2")),
        )

    def queryset(self, request, queryset):
        if self.value() == "value1":
            return queryset.filter(field="value1")
        # ...

# model_admin.py
class MyModelAdmin(OptimizedModelAdmin):
    list_filter = [MyFilter]
```

### Ajouter une Action

```python
# admin/actions.py
class MyActions:
    @staticmethod
    def my_action(modeladmin, request, queryset):
        count = queryset.update(field=value)
        messages.success(request, f"✅ {count} objet(s) mis à jour")

# model_admin.py
class MyModelAdmin(OptimizedModelAdmin):
    actions = [
        ('my_action', MyActions.my_action),
    ]

    def my_action(self, request, queryset):
        return MyActions.my_action(self, request, queryset)
    my_action.short_description = "📝 Description"
```

### Ajouter une Méthode d'Affichage

```python
# admin/displays.py
class MyDisplays:
    @staticmethod
    def my_display(obj):
        return AdminDisplay.badge(
            f"Status: {obj.status}",
            bg_color="#417690"
        )

# model_admin.py
class MyModelAdmin(OptimizedModelAdmin):
    list_display = ['my_display_method']

    def my_display_method(self, obj):
        return MyDisplays.my_display(obj)
    my_display_method.short_description = "Statut"
```

### Optimiser les QuerySets

```python
class MyModelAdmin(OptimizedModelAdmin):
    def optimize_queryset(self, qs):
        return qs.select_related(
            'foreign_key_field'
        ).prefetch_related(
            'many_to_many_field'
        )
```

## 📊 Performance

### Optimisations Intégrées

1. **QuerySets Optimisés**: `select_related` et `prefetch_related` automatiques
2. **Pas de N+1 Queries**: Chaque admin optimise ses requêtes
3. **Filtres Efficients**: Recherches indexées
4. **Pagination**: Django gère automatiquement
5. **Caching d'Affichage**: Calculs en mémoire

### Vérification Performance

```bash
# Django Debug Toolbar pour voir les queries
pip install django-debug-toolbar

# Dans settings.py
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
```

## 🧪 Tests

Exemple de test pour un admin:

```python
from django.test import TestCase
from django.contrib.admin.sites import AdminSite

class ProductAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.admin = ProductAdmin(Product, self.site)

    def test_list_display(self):
        self.assertEqual(
            len(self.admin.list_display),
            10
        )

    def test_queryset_optimization(self):
        qs = self.admin.get_queryset(None)
        # Vérifier les select_related/prefetch_related
        self.assertIn('category', qs.query.select_related)
```

## 📚 Extending the Architecture

### Ajouter un Nouveau Admin

1. Créer fichier `{model}_admin.py`
2. Créer classe admin héritant de mixins appropriés
3. Importer dans `__init__.py`
4. Ajouter affichages dans `displays.py` si nécessaire
5. Ajouter actions dans `actions.py` si nécessaire
6. Ajouter filtres dans `filters.py` si nécessaire

### Personnaliser les Utilitaires

Tous les utilitaires sont dans `utils.py` et `base.py`:
- Ajouter nouvelles méthodes à `AdminDisplay`
- Créer nouveaux mixins dans `base.py`
- Étendre filtres dans `filters.py`

## 🚀 Bonnes Pratiques

1. **Toujours optimiser les QuerySets**
2. **Utiliser les utilitaires pour l'HTML**
3. **Grouper les affichages par modèle**
4. **Séparer actions/filtres/affichages**
5. **Documenter les filtres personnalisés**
6. **Tester les actions en masse**
7. **Respecter les permissions**
8. **Fournir des messages utilisateur clairs**

## 📖 Ressources

- [Django Admin Documentation](https://docs.djangoproject.com/en/stable/ref/contrib/admin/)
- [Django Admin Patterns](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#admindocs-templatetags)
- [Django QuerySet Performance](https://docs.djangoproject.com/en/stable/topics/db/optimization/)

## 🤝 Support

Pour toute question ou amélioration, consultez la documentation des modèles et services associés.
