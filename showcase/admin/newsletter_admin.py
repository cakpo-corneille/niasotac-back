from django.contrib import admin

from ..models import (
    NewsletterSubscriber,
    NewsletterTemplate,
    NewsletterCampaign,
    NewsletterLog,
)
from .base import OptimizedModelAdmin, OptimizedTabularInline, TimestampReadOnlyMixin
from .actions import NewsletterActions
from .utils import AdminDisplay


class NewsletterLogInline(OptimizedTabularInline):
    model = NewsletterLog
    extra = 0
    fields = ['subscriber', 'status', 'created_at']
    readonly_fields = ['subscriber', 'status', 'created_at']

    def has_add_permission(self, request, obj=None):
        return False

    def optimize_queryset(self, qs):
        return qs.select_related('subscriber', 'campaign')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):

    list_display = [
        'email',
        'name',
        'confirmed_badge',
        'subscribed_badge',
        'created_at',
    ]

    list_filter = [
        'confirmed',
        'subscribed',
        'created_at',
        'confirmed_at',
    ]

    search_fields = [
        'email',
        'name',
        'tags',
    ]

    readonly_fields = [
        'confirmation_token',
        'subscriber_info',
        'created_at',
        'confirmed_at',
        'unsubscribed_at',
    ]

    fieldsets = (
        ('Informations', {
            'fields': (
                'email',
                'name',
                'ip_address',
            )
        }),
        ('Confirmation', {
            'fields': (
                'confirmed',
                'confirmation_token',
                'confirmed_at',
            ),
            'classes': ('collapse',),
        }),
        ('Abonnement', {
            'fields': (
                'subscribed',
                'unsubscribed_at',
            )
        }),
        ('Métadonnées', {
            'fields': (
                'source',
                'tags',
                'subscriber_info',
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )

    actions = [
        'mark_confirmed',
        'mark_unconfirmed',
        'unsubscribe_users',
        'subscribe_users',
    ]

    def optimize_queryset(self, qs):
        return qs.all()

    def confirmed_badge(self, obj):
        if obj.confirmed:
            return AdminDisplay.badge("✅ Confirmé", bg_color="#2e7d32")
        return AdminDisplay.badge("⏳ Non confirmé", bg_color="#f57c00")

    confirmed_badge.short_description = "Confirmation"

    def subscribed_badge(self, obj):
        if obj.subscribed:
            return AdminDisplay.badge("🔔 Abonné", bg_color="#417690")
        return AdminDisplay.badge("🔕 Désabonné", bg_color="#ccc", text_color="#666")

    subscribed_badge.short_description = "Abonnement"

    def subscriber_info(self, obj):
        info = f"<strong>Email:</strong> {obj.email}<br>"
        info += f"<strong>Inscrit:</strong> {obj.created_at.strftime('%d/%m/%Y à %H:%M')}<br>"

        if obj.confirmed_at:
            info += f"<strong>Confirmé:</strong> {obj.confirmed_at.strftime('%d/%m/%Y à %H:%M')}<br>"

        if obj.unsubscribed_at:
            info += f"<strong>Désabonné:</strong> {obj.unsubscribed_at.strftime('%d/%m/%Y à %H:%M')}<br>"

        if obj.ip_address:
            info += f"<strong>IP:</strong> {obj.ip_address}<br>"

        return AdminDisplay.info_box("👤 Détails", info)

    subscriber_info.short_description = "Informations"

    # Actions
    def mark_confirmed(self, request, queryset):
        return NewsletterActions.mark_confirmed(self, request, queryset)
    mark_confirmed.short_description = "✅ Marquer comme confirmés"

    def mark_unconfirmed(self, request, queryset):
        return NewsletterActions.mark_unconfirmed(self, request, queryset)
    mark_unconfirmed.short_description = "⏳ Marquer comme non-confirmés"

    def unsubscribe_users(self, request, queryset):
        return NewsletterActions.unsubscribe_users(self, request, queryset)
    unsubscribe_users.short_description = "🔕 Désabonner"

    def subscribe_users(self, request, queryset):
        return NewsletterActions.subscribe_users(self, request, queryset)
    subscribe_users.short_description = "🔔 Réabonner"


@admin.register(NewsletterTemplate)
class NewsletterTemplateAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):

    list_display = [
        'name',
        'is_active_badge',
        'campaigns_count',
        'updated_at',
    ]

    list_filter = [
        'is_active',
        'updated_at',
    ]

    search_fields = [
        'name',
        'slug',
        'subject',
    ]

    readonly_fields = [
        'slug',
        'campaigns_count',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Informations', {
            'fields': (
                'name',
                'slug',
                'subject',
            )
        }),
        ('Contenu', {
            'fields': (
                'plain_content',
                'html_content',
            )
        }),
        ('Configuration', {
            'fields': (
                'default_from',
                'is_active',
            ),
            'classes': ('collapse',),
        }),
        ('Campagnes', {
            'fields': (
                'campaigns_count',
            ),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def optimize_queryset(self, qs):
        from django.db.models import Count

        return qs.annotate(campaigns_count=Count('campaigns'))

    def is_active_badge(self, obj):
        if obj.is_active:
            return AdminDisplay.badge("✅ Actif", bg_color="#2e7d32")
        return AdminDisplay.badge("⏸️ Inactif", bg_color="#ccc", text_color="#666")

    is_active_badge.short_description = "Statut"

    def campaigns_count(self, obj):
        count = getattr(obj, 'campaigns_count', obj.campaigns.count())
        return AdminDisplay.badge(str(count), bg_color="#417690")

    campaigns_count.short_description = "Campagnes"


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(OptimizedModelAdmin, TimestampReadOnlyMixin):

    list_display = [
        'name',
        'template',
        'status_badge',
        'recipients_display',
        'sent_count',
        'scheduled_at',
    ]

    list_filter = [
        'status',
        'scheduled_at',
        'created_at',
    ]

    search_fields = [
        'name',
    ]

    readonly_fields = [
        'sent_count',
        'campaign_info',
        'created_at',
        'updated_at',
    ]

    fieldsets = (
        ('Informations', {
            'fields': (
                'name',
                'template',
                'status',
            )
        }),
        ('Programmation', {
            'fields': (
                'scheduled_at',
            )
        }),
        ('Destinataires', {
            'fields': (
                'subscribers',
                'recipients_display',
            )
        }),
        ('Envoi', {
            'fields': (
                'sent_count',
                'campaign_info',
            ),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',),
        }),
    )

    filter_horizontal = ['subscribers']

    inlines = [NewsletterLogInline]

    def optimize_queryset(self, qs):
        return qs.select_related('template').prefetch_related('subscribers')

    def status_badge(self, obj):
        status_map = {
            'draft': ('#e3f2fd', '#1976d2', '📝 Brouillon'),
            'scheduled': ('#fff3e0', '#f57c00', '⏰ Planifiée'),
            'sending': ('#fff3cd', '#856404', '📤 Envoi'),
            'sent': ('#e8f5e9', '#2e7d32', '✅ Envoyée'),
            'cancelled': ('#ffebee', '#c62828', '❌ Annulée'),
        }

        if obj.status in status_map:
            bg, text, label = status_map[obj.status]
            return AdminDisplay.badge(label, bg_color=bg, text_color=text)

        return obj.status

    status_badge.short_description = "Statut"

    def recipients_display(self, obj):
        count = obj.subscribers.count()
        if count == 0:
            return "Tous les abonnés confirmés"
        return f"{count} abonné(s) sélectionné(s)"

    recipients_display.short_description = "Destinataires"

    def campaign_info(self, obj):
        info = f"<strong>Statut:</strong> {obj.get_status_display()}<br>"
        info += f"<strong>Envoyé:</strong> {obj.sent_count}<br>"

        if obj.scheduled_at:
            info += f"<strong>Programmée pour:</strong> {obj.scheduled_at.strftime('%d/%m/%Y à %H:%M')}<br>"

        return AdminDisplay.info_box("📊 Détails", info)

    campaign_info.short_description = "Informations"


@admin.register(NewsletterLog)
class NewsletterLogAdmin(OptimizedModelAdmin):

    list_display = [
        'campaign',
        'subscriber_email',
        'status_badge',
        'created_at',
    ]

    list_filter = [
        'status',
        'created_at',
        'campaign',
    ]

    search_fields = [
        'subscriber__email',
        'campaign__name',
    ]

    readonly_fields = [
        'campaign',
        'subscriber',
        'status',
        'error',
        'created_at',
    ]

    fieldsets = (
        ('Informations', {
            'fields': (
                'campaign',
                'subscriber',
                'status',
            )
        }),
        ('Erreur', {
            'fields': (
                'error',
            ),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': (
                'created_at',
            ),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def optimize_queryset(self, qs):
        return qs.select_related('campaign', 'subscriber')

    def subscriber_email(self, obj):
        if obj.subscriber:
            return obj.subscriber.email
        return "—"

    subscriber_email.short_description = "Email"

    def status_badge(self, obj):
        if obj.status == 'sent':
            return AdminDisplay.badge("✅ Envoyé", bg_color="#2e7d32")
        return AdminDisplay.badge("❌ Échec", bg_color="#c62828")

    status_badge.short_description = "Statut"
