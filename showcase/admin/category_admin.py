from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from ..models import Category
from .displays import CategoryDisplays
from .actions import CategoryActions
from .base import OptimizedModelAdmin


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin, OptimizedModelAdmin):

    mptt_level_indent = 20
    mppt_indent_field = "name"

    list_display = [
        'name',
        'icon_preview',
        'level',
        'product_count_display',
        'direct_product_count_display',
        'created_at',
    ]

    list_filter = [
        'level',
        'created_at',
        'updated_at',
    ]

    search_fields = ['name', 'slug']

    prepopulated_fields = {'slug': ('name',)}

    readonly_fields = [
        'created_at',
        'updated_at',
        'icon_preview',
        'level',
        'tree_id',
    ]

    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'parent')
        }),
        ('Icône', {
            'fields': ('icon_file', 'icon_preview'),
            'classes': ('collapse',),
        }),
        ('Hiérarchie (auto)', {
            'fields': ('level', 'tree_id'),
            'classes': ('collapse',),
            'description': 'Ces champs sont gérés automatiquement par MPPT'
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    ordering = ['tree_id', 'lft']

    actions = [
        'rebuild_tree',
    ]

    def optimize_queryset(self, qs):
        return qs.select_related('parent')

    # Display methods
    def icon_preview(self, obj):
        return CategoryDisplays.icon_preview(obj)
    icon_preview.short_description = "Icône"

    def product_count_display(self, obj):
        return CategoryDisplays.product_count_display(obj)
    product_count_display.short_description = "Produits (total)"

    def direct_product_count_display(self, obj):
        return CategoryDisplays.direct_product_count_display(obj)
    direct_product_count_display.short_description = "Produits directs"

    # Actions
    def rebuild_tree(self, request, queryset):
        return CategoryActions.rebuild_tree(self, request, queryset)
    rebuild_tree.short_description = "Reconstruire l'arbre MPPT"
