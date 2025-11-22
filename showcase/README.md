# Products Module - Architecture Documentation

## Overview

This module has been completely refactored from a monolithic 1000+ line file into a clean, scalable, professional architecture following Django and Python best practices.

## Architecture Structure

```
products/
├── __init__.py
├── apps.py                      # Django app configuration
├── constants.py                 # All constants and configuration values
├── validators.py                # Custom validators
├── utils.py                     # Utility functions
├── managers.py                  # Custom managers and querysets
├── signals.py                   # Signal handlers
├── models/                      # Modular model definitions
│   ├── __init__.py
│   ├── category.py             # Category with MPTT
│   ├── product.py              # Product, ProductStatus, ProductImage
│   ├── promotion.py            # Promotion and PromotionUsage
│   ├── service.py              # Service model
│   ├── settings.py             # SiteSettings and SocialLink
│   └── newsletter.py           # Newsletter models
└── services/                    # Business logic layer
    ├── __init__.py
    ├── scoring_service.py       # Featured/Recommendation algorithms
    ├── promotion_service.py     # Promotion calculations
    └── newsletter_service.py    # Newsletter operations
```

## Key Improvements

### 1. Separation of Concerns

**Before:** All logic in model methods (1000+ lines)
**After:** Clean separation:
- Models: Data structure only
- Managers: Query logic
- Services: Business logic
- Utils: Reusable functions
- Validators: Input validation

### 2. Performance Optimizations

- Custom QuerySets with `select_related()` and `prefetch_related()`
- Optimized database indexes on frequently queried fields
- Efficient bulk operations support
- N+1 query prevention through managers

### 3. Reusability

- DRY principle applied throughout
- Shared utilities extracted (slug generation, SKU generation)
- Service classes for complex operations
- Constants centralized for easy modification

### 4. Maintainability

- Each file < 300 lines (easy to navigate)
- Clear module responsibilities
- Type hints where beneficial
- Comprehensive docstrings

### 5. Scalability

- Service layer can be extended independently
- Manager methods can be composed
- Signal handlers decoupled from models
- Easy to add new features without touching existing code

## Usage Examples

### Using Custom Managers

```python
# Get featured products with optimized queries
featured = Product.objects.featured(limit=10)

# Get products by category (including descendants)
products = Product.objects.get_queryset().by_category(category)

# Get available products only
available = Product.objects.available()
```

### Using Services

```python
from products.services import ScoringService, PromotionService

# Calculate scores
is_featured, score = ScoringService.calculate_featured_score(product_status)

# Get best promotion for a product
best_promo = PromotionService.get_best_promotion(product, quantity=2)

# Calculate final price with promotions
discount, final_price = PromotionService.calculate_price_with_promotions(product, 3)
```

### Using Validators

```python
from products.validators import validate_product_image_size

# Validators are automatically applied via model field definitions
# Can also be used manually for custom validation
```

### Using Utils

```python
from products.utils import format_price, generate_unique_slug

# Format price for display
formatted = format_price(product.price)  # "25 000 FCFA"

# Generate unique slug
slug = generate_unique_slug(Product, "New Product Name")
```

## Model Relationships

```
Category (MPTT)
    ↓ TreeForeignKey
Product
    ↓ OneToOne
ProductStatus (statistics & scoring)

Product
    ↓ ForeignKey
ProductImage (multiple)

Product ←→ ManyToMany ←→ Promotion
Category ←→ ManyToMany ←→ Promotion

NewsletterTemplate
    ↓ ForeignKey
NewsletterCampaign
    ↓ ManyToMany
NewsletterSubscriber
```

## Business Logic Flow

### Featured Product Algorithm

1. `ProductStatus` tracks views, clicks, timestamps
2. `ScoringService.calculate_featured_score()` computes score (0-100)
3. Score based on: views (30%), clicks (25%), novelty (10%), stock (15%), price (10%), margin (10%)
4. Products with score >= 70 become featured
5. Manual overrides available: `force_featured`, `exclude_from_featured`

### Promotion System

1. Multiple promotion types: percent, amount, set_price, BOGO
2. Can apply to: all products, specific products, categories (with descendants)
3. Stackable vs non-stackable promotions
4. `PromotionService` calculates best price automatically
5. Usage limits tracked per user and globally

### Newsletter System

1. Double opt-in: subscribe → confirm → active
2. Templates with variable substitution
3. Campaigns with scheduling and chunk sending
4. Detailed logging per recipient
5. Unsubscribe functionality

## Configuration

All configurable values are in `constants.py`:

- `FEATURED_SCORE_THRESHOLD = 70`
- `RECOMMENDATION_SCORE_THRESHOLD = 65`
- `MAX_IMAGES_PER_PRODUCT = 10`
- `NEW_PRODUCT_DAYS_THRESHOLD = 30`
- Score weights for algorithms
- File format lists
- Status choices

## Signals

Auto-configured in `apps.py`:

- `post_save(Product)`: Auto-create ProductStatus
- `post_save(ProductStatus)`: Auto-update scores
- `pre_delete(ProductImage)`: Delete physical files
- `pre_delete(Category)`: Delete icon files

## Testing Recommendations

```python
# Test managers
def test_featured_products_queryset():
    products = Product.objects.featured(limit=5)
    assert products.count() <= 5
    assert all(p.status.is_featured for p in products)

# Test services
def test_scoring_service():
    product_status = ProductStatus.objects.create(...)
    is_featured, score = ScoringService.calculate_featured_score(product_status)
    assert 0 <= score <= 100

# Test promotions
def test_promotion_discount():
    promotion = Promotion.objects.create(promotion_type='percent', value=20)
    discount, final = promotion.get_discount_amount(product, quantity=1)
    assert final == product.price * Decimal('0.8')
```

## Migration Notes

When migrating from the old monolithic model:

1. Import structure changes: `from products.models import Product` (unchanged)
2. Service calls: Replace model methods with service calls where applicable
3. Custom queries: Use managers instead of manual queries
4. Utils: Replace inline utility code with imported functions

## Performance Tips

1. Always use `.optimized()` queryset method for product lists
2. Use `.select_related('category', 'status')` when accessing related data
3. Use `.prefetch_related('images', 'promotions')` for reverse relations
4. Batch score recalculations using `.bulk_update()`
5. Use database-level `F()` expressions for counters

## Future Enhancements

Suggested improvements that maintain this architecture:

1. Add caching layer in services (Redis)
2. Create async tasks for score calculations (Celery)
3. Add search service (Elasticsearch integration)
4. Create API serializers module
5. Add analytics service for deeper insights
6. Implement inventory management service
7. Add product variant support

## Development Guidelines

When extending this module:

1. **Models**: Only add fields and properties, no business logic
2. **Managers**: Add query methods, always return querysets
3. **Services**: Add business logic, complex calculations
4. **Utils**: Add pure functions without side effects
5. **Validators**: Add validation logic, raise ValidationError
6. **Constants**: Add configuration values
7. **Signals**: Add auto-triggered side effects

## Support

For questions or issues with this architecture:
- Check method docstrings
- Review service implementations
- Consult manager querysets
- Reference this documentation
