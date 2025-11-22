from django.contrib import messages


class ProductActions:
    """Bulk actions for Product admin"""

    @staticmethod
    def recalculate_scores(modeladmin, request, queryset):
        from ..services.scoring_service import ScoringService

        count = 0
        for product in queryset:
            if hasattr(product, 'status'):
                product.status.recalculate_scores()
                count += 1

        messages.success(request, f"✅ Scores recalculés pour {count} produit(s)")

    @staticmethod
    def force_featured(modeladmin, request, queryset):
        count = queryset.update(
            status__force_featured=True,
            status__is_featured=True,
            status__featured_score=100.0
        )
        messages.success(request, f"⭐ {count} produit(s) forcé(s) en vedette")

    @staticmethod
    def force_recommended(modeladmin, request, queryset):
        count = queryset.update(
            status__force_recommended=True,
            status__is_recommended=True,
            status__recommendation_score=100.0
        )
        messages.success(request, f"👍 {count} produit(s) forcé(s) en recommandé")

    @staticmethod
    def exclude_from_featured(modeladmin, request, queryset):
        count = queryset.update(
            status__exclude_from_featured=True,
            status__is_featured=False
        )
        messages.success(request, f"🚫 {count} produit(s) exclu(s) des vedettes")

    @staticmethod
    def exclude_from_recommended(modeladmin, request, queryset):
        count = queryset.update(
            status__exclude_from_recommended=True,
            status__is_recommended=False
        )
        messages.success(request, f"🚫 {count} produit(s) exclu(s) des recommandations")

    @staticmethod
    def activate(modeladmin, request, queryset):
        count = queryset.update(is_active=True)
        messages.success(request, f"✅ {count} produit(s) activé(s)")

    @staticmethod
    def deactivate(modeladmin, request, queryset):
        count = queryset.update(is_active=False)
        messages.success(request, f"⏸️ {count} produit(s) désactivé(s)")

    @staticmethod
    def mark_in_stock(modeladmin, request, queryset):
        count = queryset.update(in_stock=True)
        messages.success(request, f"📦 {count} produit(s) marqué(s) en stock")

    @staticmethod
    def mark_out_of_stock(modeladmin, request, queryset):
        count = queryset.update(in_stock=False)
        messages.warning(request, f"📦 {count} produit(s) marqué(s) rupture de stock")


class CategoryActions:
    """Bulk actions for Category admin"""

    @staticmethod
    def rebuild_tree(modeladmin, request, queryset):
        from ..models import Category

        Category.objects.rebuild()
        messages.success(request, "✅ L'arbre des catégories a été reconstruit avec succès.")


class PromotionActions:
    """Bulk actions for Promotion admin"""

    @staticmethod
    def activate_promotions(modeladmin, request, queryset):
        count = queryset.update(active=True)
        messages.success(request, f"✅ {count} promotion(s) activée(s)")

    @staticmethod
    def deactivate_promotions(modeladmin, request, queryset):
        count = queryset.update(active=False)
        messages.warning(request, f"⏸️ {count} promotion(s) désactivée(s)")

    @staticmethod
    def mark_stackable(modeladmin, request, queryset):
        count = queryset.update(is_stackable=True)
        messages.info(request, f"🔗 {count} promotion(s) marquée(s) comme empilables")

    @staticmethod
    def mark_non_stackable(modeladmin, request, queryset):
        count = queryset.update(is_stackable=False)
        messages.info(request, f"🚫 {count} promotion(s) marquée(s) comme non-empilables")


class NewsletterActions:
    """Bulk actions for Newsletter admin"""

    @staticmethod
    def mark_confirmed(modeladmin, request, queryset):
        from django.utils import timezone

        count = queryset.update(confirmed=True, confirmed_at=timezone.now())
        messages.success(request, f"✅ {count} abonné(s) marqué(s) comme confirmé(s)")

    @staticmethod
    def mark_unconfirmed(modeladmin, request, queryset):
        count = queryset.update(confirmed=False)
        messages.warning(request, f"⏸️ {count} abonné(s) marqué(s) comme non-confirmé(s)")

    @staticmethod
    def unsubscribe_users(modeladmin, request, queryset):
        from django.utils import timezone

        count = queryset.update(subscribed=False, unsubscribed_at=timezone.now())
        messages.warning(request, f"🚪 {count} abonné(s) désabonné(s)")

    @staticmethod
    def subscribe_users(modeladmin, request, queryset):
        count = queryset.update(subscribed=True)
        messages.success(request, f"✅ {count} abonné(s) réabonné(s)")
