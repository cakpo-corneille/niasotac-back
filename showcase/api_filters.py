from django_filters import rest_framework as filters
from django.db import models
from .models import Product, Category, Promotion, NewsletterCampaign, NewsletterSubscriber, NewsletterTemplate
from .constants import PROMOTION_TYPES, NEWSLETTER_CAMPAIGN_STATUSES


class ProductFilter(filters.FilterSet):
    """Filtres personnalisés pour les produits"""
    
    # Filtres de base
    name = filters.CharFilter(lookup_expr='icontains')
    brand = filters.CharFilter(lookup_expr='icontains')
    category = filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_slug = filters.CharFilter(field_name='category__slug', lookup_expr='exact')
    
    # Filtres de prix
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    price_range = filters.RangeFilter(field_name='price')
    
    # Filtres de stock
    in_stock = filters.BooleanFilter()
    min_stock = filters.NumberFilter(field_name='stock_quantity', lookup_expr='gte')
    
    # Filtres de statut
    is_active = filters.BooleanFilter()
    is_featured = filters.BooleanFilter(field_name='status__is_featured')
    is_recommended = filters.BooleanFilter(field_name='status__is_recommended')
    has_discount = filters.BooleanFilter(method='filter_has_discount')
    
    # Filtres de date
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    # Recherche
    search = filters.CharFilter(method='filter_search')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('price', 'price'),
            ('created_at', 'created_at'),
            ('status__views_count', 'views_count'),
            ('status__featured_score', 'featured_score'),
        )
    )
    
    class Meta:
        model = Product
        fields = []
    
    def filter_has_discount(self, queryset, name, value):
        """Filtre les produits avec ou sans réduction"""
        if value:
            return queryset.exclude(compare_at_price__isnull=True).exclude(compare_at_price__lte=0)
        else:
            return queryset.filter(compare_at_price__isnull=True) | queryset.filter(compare_at_price__lte=0)
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom, brand, description, SKU"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(brand__icontains=value) |
            models.Q(description__icontains=value) |
            models.Q(sku__icontains=value) |
            models.Q(barcode__icontains=value)
        )


class CategoryFilter(filters.FilterSet):
    """Filtres pour les catégories"""
    
    name = filters.CharFilter(lookup_expr='icontains')
    slug = filters.CharFilter(lookup_expr='exact')
    parent = filters.ModelChoiceFilter(queryset=Category.objects.all())
    level = filters.NumberFilter()
    is_main = filters.BooleanFilter(method='filter_is_main')
    has_products = filters.BooleanFilter(method='filter_has_products')
    
    # Recherche
    search = filters.CharFilter(method='filter_search')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('level', 'level'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = Category
        fields = []
    
    def filter_is_main(self, queryset, name, value):
        """Filtre les catégories principales (sans parent)"""
        if value:
            return queryset.filter(parent__isnull=True)
        return queryset.filter(parent__isnull=False)
    
    def filter_has_products(self, queryset, name, value):
        """Filtre les catégories avec ou sans produits"""
        if value:
            return queryset.filter(products__isnull=False).distinct()
        return queryset.filter(products__isnull=True).distinct()
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom et slug"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(slug__icontains=value)
        )


class PromotionFilter(filters.FilterSet):
    """Filtres pour les promotions"""
    
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='iexact')
    promotion_type = filters.ChoiceFilter(choices=PROMOTION_TYPES)
    active = filters.BooleanFilter()
    is_stackable = filters.BooleanFilter()
    applies_to_all = filters.BooleanFilter()
    is_active_now = filters.BooleanFilter(method='filter_is_active_now')
    
    # Filtres de date
    start_after = filters.DateTimeFilter(field_name='start_at', lookup_expr='gte')
    end_before = filters.DateTimeFilter(field_name='end_at', lookup_expr='lte')
    
    # Recherche
    search = filters.CharFilter(method='filter_search')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('start_at', 'start_at'),
            ('end_at', 'end_at'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = Promotion
        fields = []
    
    def filter_is_active_now(self, queryset, name, value):
        """Filtre les promotions actuellement actives"""
        from django.utils import timezone
        now = timezone.now()
        
        if value:
            return queryset.filter(
                active=True,
                start_at__lte=now,
                end_at__gte=now
            )
        return queryset.exclude(
            active=True,
            start_at__lte=now,
            end_at__gte=now
        )
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom et code"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(code__icontains=value)
        )


class NewsletterCampaignFilter(filters.FilterSet):
    """Filtres pour les campagnes newsletter"""
    
    name = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(choices=NEWSLETTER_CAMPAIGN_STATUSES)
    template = filters.NumberFilter(field_name='template__id')
    
    # Filtres de date
    scheduled_after = filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='gte')
    scheduled_before = filters.DateTimeFilter(field_name='scheduled_at', lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('scheduled_at', 'scheduled_at'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = NewsletterCampaign
        fields = []


class NewsletterSubscriberFilter(filters.FilterSet):
    """Filtres pour les abonnés newsletter"""
    
    email = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    subscribed = filters.BooleanFilter()
    confirmed = filters.BooleanFilter()
    
    # Recherche
    search = filters.CharFilter(method='filter_search')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Recherche dans email et nom"""
        return queryset.filter(
            models.Q(email__icontains=value) |
            models.Q(name__icontains=value)
        )


class NewsletterTemplateFilter(filters.FilterSet):
    """Filtres pour les templates newsletter"""
    
    name = filters.CharFilter(lookup_expr='icontains')
    subject = filters.CharFilter(lookup_expr='icontains')
    
    # Recherche
    search = filters.CharFilter(method='filter_search')
    
    # Tri
    ordering = filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = NewsletterTemplate
        fields = []
    
    def filter_search(self, queryset, name, value):
        """Recherche dans nom et sujet"""
        return queryset.filter(
            models.Q(name__icontains=value) |
            models.Q(subject__icontains=value)
        )
