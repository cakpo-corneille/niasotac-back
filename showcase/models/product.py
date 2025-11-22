from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from mptt.models import TreeForeignKey

from ..constants import PRODUCT_IMAGE_FORMATS, MAX_IMAGES_PER_PRODUCT, NEW_PRODUCT_DAYS_THRESHOLD
from ..managers import ProductManager
from ..utils import format_price, generate_unique_slug, generate_sku, build_whatsapp_message, build_whatsapp_link
from ..validators import validate_product_image_size


class Product(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Nom du produit",
        db_index=True
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        db_index=True
    )
    description = models.TextField(verbose_name="Description")
    short_description = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Description courte"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix (FCFA)",
        db_index=True
    )
    compare_at_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix barré"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix de revient"
    )

    brand = models.CharField(
        max_length=100,
        verbose_name="Marque",
        db_index=True
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name="SKU/Référence"
    )
    barcode = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Code-barres"
    )

    category = TreeForeignKey(
        'Category',
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Catégorie"
    )

    in_stock = models.BooleanField(
        default=True,
        verbose_name="En stock",
        db_index=True
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité en stock",
        db_index=True
    )

    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name="Meta Title"
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Description"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de publication"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        db_index=True
    )

    objects = ProductManager()

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['brand', 'is_active']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        badges = []
        if hasattr(self, 'status'):
            if self.status.is_featured:
                badges.append("⭐")
            if self.status.is_recommended:
                badges.append("👍")
        if not self.in_stock:
            badges.append("📦")

        badge_str = " ".join(badges)
        return f"{badge_str} {self.name} - {self.brand}".strip()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Product, f"{self.name}-{self.brand}", max_length=220)

        if not self.sku:
            self.sku = generate_sku(self.category.slug if self.category else '', Product)

        super().save(*args, **kwargs)

    @property
    def is_new(self):
        return (timezone.now() - self.created_at).days <= NEW_PRODUCT_DAYS_THRESHOLD

    @property
    def has_discount(self):
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percent(self):
        if not self.has_discount:
            return 0
        return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)

    @property
    def display_price(self):
        return format_price(self.price)

    @property
    def display_compare_price(self):
        if self.compare_at_price:
            return format_price(self.compare_at_price)
        return None

    @property
    def effective_unit_price(self):
        from ..services.promotion_service import PromotionService
        _, final = PromotionService.calculate_price_with_promotions(self, quantity=1)
        return final

    def price_for_quantity(self, quantity=1):
        from ..services.promotion_service import PromotionService
        discount_total, final_unit = PromotionService.calculate_price_with_promotions(self, quantity=quantity)
        total_price = (final_unit * quantity).quantize(Decimal('0.01'))
        return total_price, discount_total

    def get_applicable_promotions(self):
        from ..services.promotion_service import PromotionService
        return PromotionService.get_applicable_promotions(self)

    def get_best_promotion(self, quantity=1):
        from ..services.promotion_service import PromotionService
        return PromotionService.get_best_promotion(self, quantity)

    def get_main_image(self):
        try:
            return self.images.filter(is_primary=True).first() or self.images.first()
        except Exception:
            return None

    def get_all_images(self):
        return self.images.all().order_by('-is_primary', 'order')

    def get_image_url(self):
        main_image = self.get_main_image()
        if main_image and main_image.image:
            return main_image.image.url
        return '/static/defaults/default_product.png'

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.slug])

    def get_full_url(self, request=None):
        from ..utils import build_absolute_url
        return build_absolute_url(self.get_absolute_url(), request)

    @property
    def whatsapp_link(self):
        try:
            from .settings import SiteSettings
            settings = SiteSettings.load()
            message = build_whatsapp_message(self, settings)
            return build_whatsapp_link(settings.whatsapp_number, message)
        except Exception:
            from .settings import SiteSettings
            settings = SiteSettings.load()
            return f"https://wa.me/{settings.whatsapp_number}"


class ProductStatus(models.Model):
    product = models.OneToOneField(
        'Product',
        on_delete=models.CASCADE,
        related_name='status'
    )

    view_count = models.PositiveIntegerField(default=0, verbose_name="Vues", editable=False)
    whatsapp_click_count = models.PositiveIntegerField(default=0, verbose_name="Clics WhatsApp", editable=False)
    last_viewed_at = models.DateTimeField(null=True, blank=True, editable=False)

    is_featured = models.BooleanField(
        default=False,
        verbose_name="Produit vedette",
        db_index=True
    )
    is_recommended = models.BooleanField(
        default=False,
        verbose_name="Produit recommandé",
        db_index=True
    )
    featured_score = models.FloatField(
        default=0.0,
        verbose_name="Score vedette",
        db_index=True
    )
    recommendation_score = models.FloatField(
        default=0.0,
        verbose_name="Score recommandation",
        db_index=True
    )

    force_featured = models.BooleanField(
        default=False,
        verbose_name="🔒 Forcer en vedette"
    )
    force_recommended = models.BooleanField(
        default=False,
        verbose_name="🔒 Forcer en recommandé"
    )
    exclude_from_featured = models.BooleanField(
        default=False,
        verbose_name="🚫 Exclure des vedettes"
    )
    exclude_from_recommended = models.BooleanField(
        default=False,
        verbose_name="🚫 Exclure des recommandations"
    )

    class Meta:
        verbose_name = "Statut produit"
        verbose_name_plural = "Statuts produits"
        indexes = [
            models.Index(fields=['is_featured', '-featured_score']),
            models.Index(fields=['is_recommended', '-recommendation_score']),
        ]

    def __str__(self):
        return f"Statut de {self.product.name}"

    def get_views_last_n_days(self, days=30):
        if not self.last_viewed_at:
            return 0
        days_since_view = (timezone.now() - self.last_viewed_at).days
        if days_since_view > days:
            return 0
        return min(int(self.view_count * (days / max(days_since_view, 1))), self.view_count)

    def increment_view_count(self):
        self.view_count = F('view_count') + 1
        self.last_viewed_at = timezone.now()
        self.save(update_fields=['view_count', 'last_viewed_at'])
        self.refresh_from_db()

    def increment_whatsapp_count(self):
        self.whatsapp_click_count = F('whatsapp_click_count') + 1
        self.save(update_fields=['whatsapp_click_count'])
        self.refresh_from_db()

    def recalculate_scores(self):
        from ..services.scoring_service import ScoringService

        is_featured, featured_score = ScoringService.calculate_featured_score(self)
        is_recommended, recommendation_score = ScoringService.calculate_recommendation_score(self)

        self.is_featured = is_featured
        self.featured_score = featured_score
        self.is_recommended = is_recommended
        self.recommendation_score = recommendation_score

        self.save(update_fields=[
            'is_featured',
            'featured_score',
            'is_recommended',
            'recommendation_score'
        ])


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Produit"
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/',
        validators=[
            FileExtensionValidator(allowed_extensions=PRODUCT_IMAGE_FORMATS),
            validate_product_image_size
        ],
        verbose_name="Image"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Texte alternatif"
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Image principale"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image produit"
        verbose_name_plural = "Images produit"
        ordering = ['-is_primary', 'order', 'created_at']
        indexes = [
            models.Index(fields=['product', '-is_primary', 'order']),
        ]

    def __str__(self):
        primary = "🌟 " if self.is_primary else ""
        return f"{primary}Image {self.order} - {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        if not self.pk and not self.product.images.exists():
            self.is_primary = True

        if self.product.images.count() >= MAX_IMAGES_PER_PRODUCT:
            raise ValidationError(f"Maximum {MAX_IMAGES_PER_PRODUCT} images par produit.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        was_primary = self.is_primary
        product = self.product

        super().delete(*args, **kwargs)

        if was_primary:
            next_image = product.images.first()
            if next_image:
                next_image.is_primary = True
                next_image.save()

    def get_image_url(self):
        if self.image:
            return self.image.url
        return '/static/defaults/default_product.png'
