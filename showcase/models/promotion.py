from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from ..constants import PROMOTION_TYPES
from ..managers import PromotionManager
from ..validators import validate_promotion_dates, validate_promotion_value


class Promotion(models.Model):
    PERCENT = "percent"
    AMOUNT = "amount"
    SET_PRICE = "set_price"
    BUY_X_GET_Y = "bogo"

    name = models.CharField(max_length=150, verbose_name="Nom promotion")
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Code (optionnel)"
    )
    promotion_type = models.CharField(
        max_length=20,
        choices=PROMOTION_TYPES,
        default=PERCENT
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valeur"
    )
    buy_x = models.PositiveIntegerField(default=0, verbose_name="Buy X (pour BOGO)")
    get_y = models.PositiveIntegerField(default=0, verbose_name="Get Y (pour BOGO)")

    applies_to_all = models.BooleanField(
        default=False,
        verbose_name="S'applique à tous les produits"
    )
    products = models.ManyToManyField(
        'Product',
        blank=True,
        related_name='promotions',
        verbose_name="Produits ciblés"
    )
    categories = models.ManyToManyField(
        'Category',
        blank=True,
        related_name='promotions',
        verbose_name="Catégories ciblées"
    )

    start_at = models.DateTimeField(null=True, blank=True, verbose_name="Début")
    end_at = models.DateTimeField(null=True, blank=True, verbose_name="Fin")
    active = models.BooleanField(default=True, verbose_name="Active")

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Limite d'utilisation globale"
    )
    per_user_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Limite par utilisateur"
    )

    is_stackable = models.BooleanField(
        default=False,
        verbose_name="Empilable avec d'autres promotions"
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PromotionManager()

    class Meta:
        verbose_name = "Promotion"
        verbose_name_plural = "Promotions"
        ordering = ['-start_at', 'name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['active', 'start_at', 'end_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_promotion_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            from ..utils import generate_unique_slug
            self.slug = generate_unique_slug(Promotion, self.name, max_length=180)
        super().save(*args, **kwargs)

    def clean(self):
        validate_promotion_dates(self.start_at, self.end_at)
        validate_promotion_value(self.promotion_type, self.value, self.buy_x, self.get_y)

    def is_active_now(self):
        if not self.active:
            return False

        now = timezone.now()

        if self.start_at and now < self.start_at:
            return False

        if self.end_at and now > self.end_at:
            return False

        if self.usage_limit is not None and self.usage_count() >= self.usage_limit:
            return False

        return True

    def usage_count(self):
        return self.usages.aggregate(total=models.Sum('count'))['total'] or 0

    def applies_to_product(self, product):
        if not product:
            return False

        if self.applies_to_all:
            return True

        if self.products.filter(pk=product.pk).exists():
            return True

        if product.category and self.categories.exists():
            product_ancestors = product.category.get_ancestors(include_self=True).values_list('pk', flat=True)
            if self.categories.filter(pk__in=product_ancestors).exists():
                return True

        return False

    def get_discount_amount(self, product, quantity=1):
        qty = max(1, int(quantity))
        price = product.price
        discount = Decimal('0.00')

        if not self.applies_to_product(product) or not self.is_active_now():
            return discount, price

        if self.promotion_type == self.PERCENT:
            percent = (self.value or Decimal('0')) / Decimal('100')
            discount = (price * percent) * qty
            final_unit = (price * (Decimal('1') - percent)).quantize(Decimal('0.01'))
            return discount.quantize(Decimal('0.01')), final_unit

        if self.promotion_type == self.AMOUNT:
            unit_discount = (self.value or Decimal('0')).quantize(Decimal('0.01'))
            discount = unit_discount * qty
            final_unit = max(Decimal('0.00'), price - unit_discount)
            return discount, final_unit.quantize(Decimal('0.01'))

        if self.promotion_type == self.SET_PRICE:
            set_price = (self.value or price).quantize(Decimal('0.01'))
            discount = max(Decimal('0.00'), (price - set_price) * qty)
            return discount.quantize(Decimal('0.01')), set_price

        if self.promotion_type == self.BUY_X_GET_Y:
            if self.buy_x <= 0:
                return Decimal('0.00'), price
            group = self.buy_x + self.get_y
            free_groups = qty // group
            free_units = free_groups * self.get_y
            discount = (price * free_units).quantize(Decimal('0.01'))
            return discount, price

        return Decimal('0.00'), price

    def can_user_redeem(self, user=None):
        if not self.is_active_now():
            return False

        if self.per_user_limit is None:
            return True

        if user is None:
            return True

        usage = PromotionUsage.objects.filter(promotion=self, user=user).first()
        if usage and usage.count >= self.per_user_limit:
            return False

        return True


class PromotionUsage(models.Model):
    promotion = models.ForeignKey(
        Promotion,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='promotion_usages'
    )
    count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Utilisation promotion"
        verbose_name_plural = "Utilisations promotions"
        indexes = [
            models.Index(fields=['promotion', 'user']),
        ]
        unique_together = [['promotion', 'user']]

    def __str__(self):
        who = self.user.username if self.user else "ANONYME/GLOBAL"
        return f"{self.promotion.name} - {who}: {self.count}"
