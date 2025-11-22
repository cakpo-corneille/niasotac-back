from django.contrib import admin

from ..models import Promotion, PromotionUsage
from .base import OptimizedModelAdmin, OptimizedTabularInline, TimestampReadOnlyMixin
from .actions import PromotionActions
from .utils import AdminDisplay


class PromotionUsageInline(OptimizedTabularInline):
    model = PromotionUsage
    extra = 0
    fields = ['user', 'count', 'last_used_at']
    readonly_fields = ['user', 'count', 'last_used_at']

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def optimize_queryset(self, qs):
        return qs.select_related('user', 'promotion')


@admin.register(Promotion)
class PromotionAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):

    list_display = [
        'name',
        'promotion_type_display',
        'value_display',
        'is_active_badge',
        'stackable_badge',
        'date_range_display',
        'usage_display',
    ]

    list_filter = [
        'active',
        'promotion_type',
        'is_stackable',
        'start_at',
        'end_at',
        'applies_to_all',
    ]

    search_fields = [
        'name',
        'code',
        'slug',
    ]

    readonly_fields = [
        'slug',
        'promotion_info',
        'usage_stats',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('🎯 Informations principales', {
            'fields': (
                'name',
                'slug',
                'code',
                'promotion_type',
            )
        }),
        ('💰 Valeur', {
            'fields': (
                'value',
                'buy_x',
                'get_y',
            ),
            'description': 'Configurez selon le type de promotion'
        }),
        ('🎁 Applicabilité', {
            'fields': (
                'applies_to_all',
                'products',
                'categories',
            )
        }),
        ('📅 Programmation', {
            'fields': (
                'start_at',
                'end_at',
                'active',
            )
        }),
        ('🔗 Empilement', {
            'fields': (
                'is_stackable',
            ),
            'description': 'Peut-elle être combinée avec d\'autres promotions?'
        }),
        ('⚙️ Limites d\'utilisation', {
            'fields': (
                'usage_limit',
                'per_user_limit',
            ),
            'classes': ('collapse',),
        }),
        ('📊 Informations', {
            'fields': (
                'promotion_info',
                'usage_stats',
            ),
            'classes': ('collapse',),
        }),
        ('📝 Métadonnées', {
            'fields': (
                'created_by',
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    filter_horizontal = ['products', 'categories']

    inlines = [PromotionUsageInline]

    actions = [
        'activate_promotions',
        'deactivate_promotions',
        'mark_stackable',
        'mark_non_stackable',
    ]

    def optimize_queryset(self, qs):
        return qs.select_related('created_by').prefetch_related('products', 'categories')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    # Display methods
    def promotion_type_display(self, obj):
        type_map = {
            'percent': ('📊 Pourcentage', '#417690'),
            'amount': ('💰 Montant fixe', '#2e7d32'),
            'set_price': ('🏷️ Prix fixé', '#f57c00'),
            'bogo': ('🎁 Buy X Get Y', '#1976d2'),
        }

        if obj.promotion_type in type_map:
            label, color = type_map[obj.promotion_type]
            return AdminDisplay.badge(label, bg_color=color)
        return obj.promotion_type

    promotion_type_display.short_description = "Type"

    def value_display(self, obj):
        if obj.promotion_type == 'percent' and obj.value:
            return AdminDisplay.badge(f"{obj.value}%")
        elif obj.promotion_type == 'amount' and obj.value:
            return AdminDisplay.badge(f"{obj.value} FCFA")
        elif obj.promotion_type == 'set_price' and obj.value:
            return AdminDisplay.badge(f"{obj.value} FCFA")
        elif obj.promotion_type == 'bogo':
            return AdminDisplay.badge(f"Buy {obj.buy_x} Get {obj.get_y}")
        return "—"

    value_display.short_description = "Valeur"

    def is_active_badge(self, obj):
        if obj.is_active_now():
            return AdminDisplay.badge("✅ Actif", bg_color="#2e7d32")
        elif obj.active:
            return AdminDisplay.badge("⏰ Programmée", bg_color="#f57c00")
        else:
            return AdminDisplay.badge("⏸️ Inactive", bg_color="#ccc", text_color="#666")

    is_active_badge.short_description = "Statut"

    def stackable_badge(self, obj):
        if obj.is_stackable:
            return AdminDisplay.badge("🔗 Empilable")
        return AdminDisplay.badge("🚫 Seule", bg_color="#f5f5f5", text_color="#999")

    stackable_badge.short_description = "Empilement"

    def date_range_display(self, obj):
        if obj.start_at and obj.end_at:
            return f"{obj.start_at.strftime('%d/%m')} - {obj.end_at.strftime('%d/%m')}"
        elif obj.start_at:
            return f"À partir de {obj.start_at.strftime('%d/%m/%Y')}"
        elif obj.end_at:
            return f"Jusqu'au {obj.end_at.strftime('%d/%m/%Y')}"
        return "—"

    date_range_display.short_description = "Période"

    def usage_display(self, obj):
        used = obj.usage_count()
        limit = obj.usage_limit or "∞"
        return f"{used}/{limit}"

    usage_display.short_description = "Utilisation"

    def promotion_info(self, obj):
        info_parts = []
        info_parts.append(f"<strong>Type:</strong> {obj.get_promotion_type_display()}<br>")

        if obj.applies_to_all:
            info_parts.append("<strong>Applicabilité:</strong> Tous les produits<br>")
        else:
            products_count = obj.products.count()
            categories_count = obj.categories.count()
            if products_count > 0:
                info_parts.append(f"<strong>Produits:</strong> {products_count}<br>")
            if categories_count > 0:
                info_parts.append(f"<strong>Catégories:</strong> {categories_count}<br>")

        if obj.code:
            info_parts.append(f"<strong>Code:</strong> {obj.code}<br>")

        return AdminDisplay.info_box("📋 Détails", "".join(info_parts))

    promotion_info.short_description = "Informations"

    def usage_stats(self, obj):
        total_used = obj.usage_count()
        usage_objs = obj.usages.all()

        info = f"<strong>Total utilisé:</strong> {total_used}<br>"

        if obj.usage_limit:
            remaining = obj.usage_limit - total_used
            percentage = (total_used / obj.usage_limit * 100) if obj.usage_limit > 0 else 0
            info += f"<strong>Limite:</strong> {obj.usage_limit}<br>"
            info += f"<strong>Restant:</strong> {remaining}<br>"
            info += f"<strong>Utilisation:</strong> {percentage:.1f}%<br>"

        return AdminDisplay.info_box("📊 Utilisation", info)

    usage_stats.short_description = "Statistiques d'utilisation"

    # Actions
    def activate_promotions(self, request, queryset):
        return PromotionActions.activate_promotions(self, request, queryset)
    activate_promotions.short_description = "✅ Activer les promotions"

    def deactivate_promotions(self, request, queryset):
        return PromotionActions.deactivate_promotions(self, request, queryset)
    deactivate_promotions.short_description = "⏸️ Désactiver les promotions"

    def mark_stackable(self, request, queryset):
        return PromotionActions.mark_stackable(self, request, queryset)
    mark_stackable.short_description = "🔗 Marquer comme empilables"

    def mark_non_stackable(self, request, queryset):
        return PromotionActions.mark_non_stackable(self, request, queryset)
    mark_non_stackable.short_description = "🚫 Marquer comme non-empilables"
