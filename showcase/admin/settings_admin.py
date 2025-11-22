from django.contrib import admin

from ..models import SiteSettings, SocialLink, Service
from .base import OptimizedModelAdmin, SingletonAdminMixin, UserTrackingMixin


@admin.register(SocialLink)
class SocialLinkAdmin(OptimizedModelAdmin):

    list_display = ['name', 'url']
    search_fields = ['name', 'url']


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdminMixin, UserTrackingMixin, OptimizedModelAdmin):

    fieldsets = (
        ('📱 Informations de contact', {
            'fields': (
                'whatsapp_number',
                'contact_phone',
                'contact_email',
                'contact_address'
            )
        }),
        ('🏢 Informations de l\'entreprise', {
            'fields': (
                'company_name',
                'company_description'
            )
        }),
        ('🌍 Réseaux sociaux', {
            'fields': (
                'social_links',
            )
        }),
        ('📝 Métadonnées', {
            'fields': (
                'updated_at',
                'updated_by',
            ),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ['updated_at', 'updated_by']
    filter_horizontal = ['social_links']


@admin.register(Service)
class ServiceAdmin(OptimizedModelAdmin):

    list_display = [
        'title',
        'is_active_badge',
        'order',
        'created_at',
    ]

    list_filter = [
        'is_active',
        'created_at',
    ]

    search_fields = [
        'title',
        'description',
    ]

    prepopulated_fields = {'slug': ('title',)}

    readonly_fields = [
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Informations', {
            'fields': (
                'title',
                'slug',
                'description',
                'image',
            )
        }),
        ('Configuration', {
            'fields': (
                'order',
                'is_active',
                'external_link',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    ordering = ['order', 'title']

    def is_active_badge(self, obj):
        from .utils import AdminDisplay

        if obj.is_active:
            return AdminDisplay.badge("✅ Actif", bg_color="#2e7d32")
        return AdminDisplay.badge("⏸️ Inactif", bg_color="#ccc", text_color="#666")

    is_active_badge.short_description = "Statut"
