from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from .constants import FEATURED_SCORE_THRESHOLD, RECOMMENDATION_SCORE_THRESHOLD, NEW_PRODUCT_DAYS_THRESHOLD


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def in_stock(self):
        return self.filter(in_stock=True, stock_quantity__gt=0)

    def available(self):
        return self.active().in_stock()

    def featured(self):
        return self.filter(
            status__is_featured=True,
            is_active=True,
            in_stock=True
        ).select_related('category', 'status').prefetch_related('images')

    def recommended(self):
        return self.filter(
            status__is_recommended=True,
            is_active=True,
            in_stock=True
        ).select_related('category', 'status').prefetch_related('images')

    def new_arrivals(self, days=NEW_PRODUCT_DAYS_THRESHOLD):
        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            created_at__gte=cutoff_date,
            is_active=True,
            in_stock=True
        ).select_related('category').prefetch_related('images')

    def best_sellers(self):
        return self.filter(
            is_active=True,
            in_stock=True
        ).select_related('category', 'status').prefetch_related('images').order_by(
            '-status__whatsapp_click_count',
            '-status__view_count'
        )

    def by_category(self, category):
        descendant_ids = category.get_descendants(include_self=True).values_list('id', flat=True)
        return self.filter(category_id__in=descendant_ids)

    def with_discount(self):
        return self.filter(
            compare_at_price__isnull=False,
            compare_at_price__gt=F('price')
        )

    def optimized(self):
        return self.select_related('category', 'status').prefetch_related('images', 'promotions')


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def available(self):
        return self.get_queryset().available()

    def featured(self, limit=10):
        return self.get_queryset().featured().order_by(
            '-status__featured_score',
            '-created_at'
        )[:limit]

    def recommended(self, limit=10, exclude_ids=None):
        qs = self.get_queryset().recommended()
        if exclude_ids:
            qs = qs.exclude(id__in=exclude_ids)
        return qs.order_by(
            '-status__recommendation_score',
            '-created_at'
        )[:limit]

    def new_arrivals(self, limit=10):
        return self.get_queryset().new_arrivals().order_by('-created_at')[:limit]

    def best_sellers(self, limit=10):
        return self.get_queryset().best_sellers()[:limit]


class CategoryQuerySet(models.QuerySet):
    def with_product_count(self):
        return self.annotate(
            direct_products=Count('products', filter=Q(products__is_active=True))
        )

    def root_categories(self):
        return self.filter(parent__isnull=True)

    def active_with_products(self):
        return self.filter(products__is_active=True).distinct()


class CategoryManager(models.Manager):
    def get_queryset(self):
        return CategoryQuerySet(self.model, using=self._db)

    def root_categories(self):
        return self.get_queryset().root_categories()

    def with_product_count(self):
        return self.get_queryset().with_product_count()


class PromotionQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            active=True,
            start_at__lte=now,
            end_at__gte=now
        ) | self.filter(
            active=True,
            start_at__isnull=True,
            end_at__isnull=True
        ) | self.filter(
            active=True,
            start_at__lte=now,
            end_at__isnull=True
        ) | self.filter(
            active=True,
            start_at__isnull=True,
            end_at__gte=now
        )

    def for_product(self, product):
        now = timezone.now()
        base_qs = self.filter(active=True)

        all_products = base_qs.filter(applies_to_all=True)
        specific_products = base_qs.filter(products=product)

        product_ancestors = product.category.get_ancestors(include_self=True).values_list('pk', flat=True)
        category_promotions = base_qs.filter(categories__pk__in=product_ancestors)

        return (all_products | specific_products | category_promotions).distinct()


class PromotionManager(models.Manager):
    def get_queryset(self):
        return PromotionQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def for_product(self, product):
        return self.get_queryset().for_product(product)


class NewsletterSubscriberQuerySet(models.QuerySet):
    def subscribed(self):
        return self.filter(subscribed=True)

    def confirmed(self):
        return self.filter(confirmed=True, subscribed=True)

    def unconfirmed(self):
        return self.filter(confirmed=False, subscribed=True)


class NewsletterSubscriberManager(models.Manager):
    def get_queryset(self):
        return NewsletterSubscriberQuerySet(self.model, using=self._db)

    def subscribed(self):
        return self.get_queryset().subscribed()

    def confirmed(self):
        return self.get_queryset().confirmed()
