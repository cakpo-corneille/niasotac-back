from django.contrib.admin import SimpleListFilter, DateFieldListFilter
from django.utils.translation import gettext_lazy as _


class StockStatusFilter(SimpleListFilter):
    title = _("Statut du stock")
    parameter_name = "stock_status"

    def lookups(self, request, model_admin):
        return (
            ("in_stock", _("En stock")),
            ("low_stock", _("Stock faible")),
            ("out_of_stock", _("Rupture")),
        )

    def queryset(self, request, queryset):
        if self.value() == "in_stock":
            return queryset.filter(in_stock=True, stock_quantity__gt=10)
        if self.value() == "low_stock":
            return queryset.filter(in_stock=True, stock_quantity__lte=10, stock_quantity__gt=0)
        if self.value() == "out_of_stock":
            return queryset.filter(stock_quantity=0)


class PriceRangeFilter(SimpleListFilter):
    title = _("Gamme de prix")
    parameter_name = "price_range"

    def lookups(self, request, model_admin):
        return (
            ("<10k", _("Moins de 10k FCFA")),
            ("10k-50k", _("10k - 50k FCFA")),
            ("50k-100k", _("50k - 100k FCFA")),
            (">100k", _("Plus de 100k FCFA")),
        )

    def queryset(self, request, queryset):
        if self.value() == "<10k":
            return queryset.filter(price__lt=10000)
        if self.value() == "10k-50k":
            return queryset.filter(price__gte=10000, price__lt=50000)
        if self.value() == "50k-100k":
            return queryset.filter(price__gte=50000, price__lt=100000)
        if self.value() == ">100k":
            return queryset.filter(price__gte=100000)


class DiscountFilter(SimpleListFilter):
    title = _("Réductions")
    parameter_name = "has_discount"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("Avec réduction")),
            ("no", _("Sans réduction")),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(
                compare_at_price__isnull=False,
                compare_at_price__gt__field='price'
            )
        if self.value() == "no":
            return queryset.filter(
                compare_at_price__isnull=True
            ) | queryset.filter(compare_at_price__lte__field='price')


class NewProductFilter(SimpleListFilter):
    title = _("Nouveaux produits")
    parameter_name = "is_new"

    def lookups(self, request, model_admin):
        return (
            ("7days", _("Moins de 7 jours")),
            ("30days", _("Moins de 30 jours")),
            ("90days", _("Moins de 90 jours")),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()

        if self.value() == "7days":
            cutoff = now - timedelta(days=7)
            return queryset.filter(created_at__gte=cutoff)
        if self.value() == "30days":
            cutoff = now - timedelta(days=30)
            return queryset.filter(created_at__gte=cutoff)
        if self.value() == "90days":
            cutoff = now - timedelta(days=90)
            return queryset.filter(created_at__gte=cutoff)


class EngagementFilter(SimpleListFilter):
    title = _("Engagement")
    parameter_name = "engagement"

    def lookups(self, request, model_admin):
        return (
            ("high", _("Haute (100+ engagements)")),
            ("medium", _("Moyenne (20-100)")),
            ("low", _("Faible (< 20)")),
            ("none", _("Aucun")),
        )

    def queryset(self, request, queryset):
        if self.value() == "high":
            return queryset.filter(status__view_count__gte=100)
        if self.value() == "medium":
            return queryset.filter(status__view_count__gte=20, status__view_count__lt=100)
        if self.value() == "low":
            return queryset.filter(status__view_count__gt=0, status__view_count__lt=20)
        if self.value() == "none":
            return queryset.filter(status__view_count=0)


class CategoryLevelFilter(SimpleListFilter):
    title = _("Niveau de catégorie")
    parameter_name = "level"

    def lookups(self, request, model_admin):
        return (
            ("0", _("Catégories principales")),
            ("1", _("Sous-catégories")),
            ("2", _("Catégories tertaines")),
        )

    def queryset(self, request, queryset):
        if self.value() in ["0", "1", "2"]:
            return queryset.filter(level=int(self.value()))
