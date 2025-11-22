from django.utils.html import format_html
from .utils import AdminDisplay


class ProductDisplays:
    """Display methods for Product admin"""

    @staticmethod
    def thumbnail(obj):
        main_image = obj.get_main_image()
        return AdminDisplay.image_thumbnail(
            main_image.image.url if main_image and main_image.image else None,
            alt_text=obj.name
        )

    @staticmethod
    def main_image_preview(obj):
        main_image = obj.get_main_image()

        if main_image and main_image.image:
            return format_html(
                '<div style="padding:15px; background:#f8f9fa; border-radius:8px;">'
                '<img src="{}" style="max-width:300px; max-height:300px; '
                'display:block; border-radius:4px; box-shadow:0 2px 8px rgba(0,0,0,0.1);" />'
                '<p style="margin-top:10px; color:#666; font-size:12px;">'
                '✅ Image principale définie</p>'
                '</div>',
                main_image.image.url
            )
        return AdminDisplay.alert("Aucune image principale. Ajoutez des images ci-dessous.", "error")

    @staticmethod
    def gallery_preview(obj):
        images = obj.get_all_images()

        if not images:
            return format_html('<p style="color:#999;">Aucune image</p>')

        image_data = []
        for img in images:
            image_data.append({
                "url": img.image.url if img.image else "",
                "title": img.alt_text or "",
                "badge": "🌟" if img.is_primary else f"#{img.order}",
                "border": "#417690" if img.is_primary else "#ddd",
            })

        return AdminDisplay.gallery(image_data)

    @staticmethod
    def formatted_price(obj):
        if obj.has_discount:
            return format_html(
                '<div style="line-height:1.4;">'
                '<span style="color:#d32f2f; font-weight:bold;">{}</span><br>'
                '<span style="text-decoration:line-through; color:#999; font-size:11px;">{}</span> '
                '<span style="background:#e8f5e9; color:#2e7d32; padding:2px 6px; '
                'border-radius:3px; font-size:10px; font-weight:bold;">-{}%</span>'
                '</div>',
                obj.display_price,
                obj.display_compare_price,
                obj.discount_percent
            )
        return format_html(
            '<span style="font-weight:bold;">{}</span>',
            obj.display_price
        )

    @staticmethod
    def stock_status(obj):
        if obj.stock_quantity == 0:
            return AdminDisplay.badge("📦 Rupture", bg_color="#ffebee", text_color="#c62828")
        elif obj.stock_quantity <= 10:
            return AdminDisplay.badge(
                f"⚠️ Stock faible ({obj.stock_quantity})",
                bg_color="#fff3e0",
                text_color="#f57c00"
            )
        else:
            return AdminDisplay.badge(
                f"✅ En stock ({obj.stock_quantity})",
                bg_color="#e8f5e9",
                text_color="#2e7d32"
            )

    @staticmethod
    def featured_badge(obj):
        if obj.status.is_featured:
            icon = "🔒" if obj.status.force_featured else "⭐"
            return format_html(
                '<div style="text-align:center;">'
                '<span style="background:#fff3e0; color:#f57c00; padding:4px 8px; '
                'border-radius:4px; font-size:11px; font-weight:bold;">{} Vedette</span><br>'
                '<span style="font-size:10px; color:#666;">Score: {:.1f}</span>'
                '</div>',
                icon, obj.status.featured_score
            )
        elif obj.status.exclude_from_featured:
            return AdminDisplay.badge("🚫 Exclu", bg_color="#f5f5f5", text_color="#999")
        else:
            return format_html(
                '<span style="color:#ccc; font-size:11px;">— ({:.1f})</span>',
                obj.status.featured_score
            )

    @staticmethod
    def recommended_badge(obj):
        if obj.status.is_recommended:
            icon = "🔒" if obj.status.force_recommended else "👍"
            return format_html(
                '<div style="text-align:center;">'
                '<span style="background:#e3f2fd; color:#1976d2; padding:4px 8px; '
                'border-radius:4px; font-size:11px; font-weight:bold;">{} Recommandé</span><br>'
                '<span style="font-size:10px; color:#666;">Score: {:.1f}</span>'
                '</div>',
                icon, obj.status.recommendation_score
            )
        elif obj.status.exclude_from_recommended:
            return AdminDisplay.badge("🚫 Exclu", bg_color="#f5f5f5", text_color="#999")
        else:
            return format_html(
                '<span style="color:#ccc; font-size:11px;">— ({:.1f})</span>',
                obj.status.recommendation_score
            )

    @staticmethod
    def stats_display(obj):
        return format_html(
            '<div style="font-size:11px; line-height:1.6;">'
            '👁️ {} vues<br>'
            '💬 {} clics<br>'
            '{}'
            '</div>',
            obj.status.view_count,
            obj.status.whatsapp_click_count,
            "🆕 Nouveau" if obj.is_new else ""
        )

    @staticmethod
    def whatsapp_link_display(obj):
        return AdminDisplay.button(
            "Tester le lien WhatsApp",
            obj.whatsapp_link,
            style="success"
        )

    @staticmethod
    def algorithm_info(obj):
        from ..constants import FEATURED_SCORE_THRESHOLD, RECOMMENDATION_SCORE_THRESHOLD

        days_since_creation = (obj.created_at.now() - obj.created_at).days if hasattr(obj.created_at, 'now') else 0

        info = format_html(
            '<div style="background:#f5f5f5; padding:15px; border-radius:8px; '
            'font-size:12px; line-height:1.8;">'
            '<h4 style="margin-top:0; margin-bottom:10px;">📊 Détails des algorithmes</h4>'

            '<strong>⭐ Produit Vedette (seuil: {})</strong><br>'
            '• Score actuel: <strong>{:.2f}/100</strong><br>'
            '• Statut: {}<br>'
            '• Vues (30j): {} | Clics WhatsApp: {}<br>'
            '• Stock: {} | Ancienneté: {} jours<br><br>'

            '<strong>👍 Produit Recommandé (seuil: {})</strong><br>'
            '• Score actuel: <strong>{:.2f}/100</strong><br>'
            '• Statut: {}<br>'
            '• Engagement total: {}<br><br>'

            '<p style="color:#666; font-style:italic; margin-bottom:0;">'
            '💡 Les scores sont recalculés automatiquement. '
            'Utilisez les "Contrôles manuels" pour forcer ou exclure.'
            '</p>'
            '</div>',
            FEATURED_SCORE_THRESHOLD,
            obj.status.featured_score,
            "✅ VEDETTE" if obj.status.is_featured else "❌ Non vedette",
            obj.status.get_views_last_n_days(30),
            obj.status.whatsapp_click_count,
            obj.stock_quantity,
            days_since_creation,
            RECOMMENDATION_SCORE_THRESHOLD,
            obj.status.recommendation_score,
            "✅ RECOMMANDÉ" if obj.status.is_recommended else "❌ Non recommandé",
            obj.status.view_count + (obj.status.whatsapp_click_count * 3)
        )

        return info


class CategoryDisplays:
    """Display methods for Category admin"""

    @staticmethod
    def icon_preview(obj):
        return AdminDisplay.image_thumbnail(
            obj.icon_file.url if obj.icon_file else None,
            alt_text=obj.name,
            width=32,
            height=32
        )

    @staticmethod
    def product_count_display(obj):
        count = obj.product_count
        return AdminDisplay.badge(
            f"📦 {count}",
            bg_color="#417690" if count > 0 else "#f5f5f5",
            text_color="white" if count > 0 else "#999"
        )

    @staticmethod
    def direct_product_count_display(obj):
        count = obj.direct_product_count
        return AdminDisplay.badge(
            f"{count}",
            bg_color="#79aec8" if count > 0 else "#f5f5f5",
            text_color="white" if count > 0 else "#999"
        )


class ImageDisplays:
    """Display methods for ProductImage admin"""

    @staticmethod
    def thumbnail(obj):
        return AdminDisplay.image_thumbnail(
            obj.image.url if obj.image else None,
            alt_text=obj.alt_text,
            width=60,
            height=60
        )
