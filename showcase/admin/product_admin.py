from django.contrib import admin

from ..models import Product, ProductImage
from .base import OptimizedModelAdmin, OptimizedTabularInline, TimestampReadOnlyMixin
from .displays import ProductDisplays, ImageDisplays
from .actions import ProductActions
from .filters import (
    StockStatusFilter,
    PriceRangeFilter,
    DiscountFilter,
    NewProductFilter,
    EngagementFilter,
)


class ProductImageInline(OptimizedTabularInline):
    model = ProductImage
    extra = 1
    max_num = 10
    fields = ['image_preview', 'image', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['image_preview']

    def optimize_queryset(self, qs):
        return qs.select_related('product')

    def image_preview(self, obj):
        return ImageDisplays.thumbnail(obj)
    image_preview.short_description = "Aperçu"


@admin.register(ProductImage)
class ProductImageAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):
    list_display = ['image_preview', 'product', 'is_primary', 'order', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['product__name', 'alt_text']
    list_editable = ['is_primary', 'order']

    def optimize_queryset(self, qs):
        return qs.select_related('product')

    def image_preview(self, obj):
        return ImageDisplays.thumbnail(obj)
    image_preview.short_description = "Aperçu"


@admin.register(Product)
class ProductAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):

    list_display = [
        'product_thumbnail',
        'name',
        'brand',
        'category',
        'formatted_price',
        'stock_status',
        'featured_badge',
        'recommended_badge',
        'stats_display',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'in_stock',
        StockStatusFilter,
        PriceRangeFilter,
        DiscountFilter,
        NewProductFilter,
        EngagementFilter,
        'category',
        'brand',
        ('created_at', admin.DateFieldListFilter),
    ]

    search_fields = [
        'name',
        'brand',
        'sku',
        'barcode',
        'description',
    ]

    readonly_fields = [
        'main_image_preview',
        'gallery_preview',
        'sku',
        'slug',
        'whatsapp_link_display',
        'algorithm_info',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('🎯 Informations principales', {
            'fields': (
                'name',
                'brand',
                'sku',
                'barcode',
                'category',
            )
        }),
        ('📝 Description', {
            'fields': (
                'short_description',
                'description',
            )
        }),
        ('💰 Prix', {
            'fields': (
                'price',
                'compare_at_price',
                'cost_price',
            ),
            'description': 'Le prix barré permet d\'afficher une réduction'
        }),
        ('📦 Stock', {
            'fields': (
                'stock_quantity',
                'in_stock',
            )
        }),
        ('🖼️ Images', {
            'fields': (
                'main_image_preview',
                'gallery_preview',
            ),
            'description': 'Gérez les images dans la section "Images produit" ci-dessous'
        }),
        ('⭐ Statuts automatiques (Algorithmes)', {
            'fields': (
                'algorithm_info',
            ),
            'classes': ('collapse',),
            'description': 'Ces valeurs sont calculées automatiquement'
        }),
        ('🔒 Contrôles manuels (Override)', {
            'fields': (
                ('status', ),
            ),
            'classes': ('collapse',),
            'description': 'Forcer ou exclure des algorithmes automatiques'
        }),
        ('🔗 WhatsApp', {
            'fields': (
                'whatsapp_link_display',
            ),
            'classes': ('collapse',),
        }),
        ('🔍 SEO', {
            'fields': (
                'meta_title',
                'meta_description',
            ),
            'classes': ('collapse',),
        }),
        ('⚙️ Paramètres', {
            'fields': (
                'is_active',
                'published_at',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    inlines = [ProductImageInline]

    actions = [
        'recalculate_scores',
        'force_featured',
        'force_recommended',
        'exclude_from_featured',
        'exclude_from_recommended',
        'activate',
        'deactivate',
        'mark_in_stock',
        'mark_out_of_stock',
    ]

    def optimize_queryset(self, qs):
        return qs.select_related('category', 'status').prefetch_related('images')

    # Display methods
    def product_thumbnail(self, obj):
        return ProductDisplays.thumbnail(obj)
    product_thumbnail.short_description = "Image"

    def main_image_preview(self, obj):
        return ProductDisplays.main_image_preview(obj)
    main_image_preview.short_description = "Aperçu image principale"

    def gallery_preview(self, obj):
        return ProductDisplays.gallery_preview(obj)
    gallery_preview.short_description = "Galerie d'images"

    def formatted_price(self, obj):
        return ProductDisplays.formatted_price(obj)
    formatted_price.short_description = "Prix"
    formatted_price.admin_order_field = 'price'

    def stock_status(self, obj):
        return ProductDisplays.stock_status(obj)
    stock_status.short_description = "Stock"

    def featured_badge(self, obj):
        return ProductDisplays.featured_badge(obj)
    featured_badge.short_description = "Vedette"

    def recommended_badge(self, obj):
        return ProductDisplays.recommended_badge(obj)
    recommended_badge.short_description = "Recommandé"

    def stats_display(self, obj):
        return ProductDisplays.stats_display(obj)
    stats_display.short_description = "Stats"

    def whatsapp_link_display(self, obj):
        return ProductDisplays.whatsapp_link_display(obj)
    whatsapp_link_display.short_description = "Prévisualisation WhatsApp"

    def algorithm_info(self, obj):
        return ProductDisplays.algorithm_info(obj)
    algorithm_info.short_description = "Analyse algorithmique"

    # Actions
    def recalculate_scores(self, request, queryset):
        return ProductActions.recalculate_scores(self, request, queryset)
    recalculate_scores.short_description = "🔄 Recalculer les scores des algorithmes"

    def force_featured(self, request, queryset):
        return ProductActions.force_featured(self, request, queryset)
    force_featured.short_description = "⭐ Forcer comme vedette"

    def force_recommended(self, request, queryset):
        return ProductActions.force_recommended(self, request, queryset)
    force_recommended.short_description = "👍 Forcer comme recommandé"

    def exclude_from_featured(self, request, queryset):
        return ProductActions.exclude_from_featured(self, request, queryset)
    exclude_from_featured.short_description = "🚫 Exclure des vedettes"

    def exclude_from_recommended(self, request, queryset):
        return ProductActions.exclude_from_recommended(self, request, queryset)
    exclude_from_recommended.short_description = "🚫 Exclure des recommandations"

    def activate(self, request, queryset):
        return ProductActions.activate(self, request, queryset)
    activate.short_description = "✅ Activer les produits"

    def deactivate(self, request, queryset):
        return ProductActions.deactivate(self, request, queryset)
    deactivate.short_description = "⏸️ Désactiver les produits"

    def mark_in_stock(self, request, queryset):
        return ProductActions.mark_in_stock(self, request, queryset)
    mark_in_stock.short_description = "📦 Marquer en stock"

    def mark_out_of_stock(self, request, queryset):
        return ProductActions.mark_out_of_stock(self, request, queryset)
    mark_out_of_stock.short_description = "📦 Marquer rupture"
