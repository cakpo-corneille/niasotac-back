from django.utils.html import format_html
from django.utils.safestring import mark_safe


class AdminDisplay:
    """Utilities for HTML rendering in admin"""

    @staticmethod
    def image_thumbnail(image_url, alt_text="", width=60, height=60, border_color="#ddd"):
        if not image_url:
            return format_html(
                '<div style="width:{}px; height:{}px; background:#f0f0f0; '
                'border-radius:4px; display:flex; align-items:center; '
                'justify-content:center; color:#999; font-size:10px;">'
                'Pas d\'image</div>',
                width, height
            )
        return format_html(
            '<img src="{}" alt="{}" style="max-height:{}px; max-width:{}px; '
            'object-fit:contain; border-radius:4px; border:1px solid {};" />',
            image_url, alt_text, height, width, border_color
        )

    @staticmethod
    def badge(text, bg_color="#417690", text_color="white", size="11px"):
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 8px; '
            'border-radius:4px; font-size:{}; font-weight:bold; white-space:nowrap;">{}</span>',
            bg_color, text_color, size, text
        )

    @staticmethod
    def status_badge(status, status_map):
        if status not in status_map:
            return "—"
        bg, text, label = status_map[status]
        return AdminDisplay.badge(label, bg_color=bg, text_color=text)

    @staticmethod
    def info_box(title, content, bg_color="#f5f5f5"):
        return format_html(
            '<div style="background:{}; padding:15px; border-radius:8px; '
            'font-size:12px; line-height:1.8;">'
            '<h4 style="margin-top:0; margin-bottom:10px;">{}</h4>'
            '{}'
            '</div>',
            bg_color, title, mark_safe(content)
        )

    @staticmethod
    def gallery(images, max_width=100, max_height=100):
        if not images:
            return format_html('<p style="color:#999;">Aucune image</p>')

        html_parts = ['<div style="display:flex; gap:10px; flex-wrap:wrap; align-items:flex-start;">']

        for idx, img in enumerate(images):
            html_parts.append(
                f'<div style="position:relative;">'
                f'<img src="{img["url"]}" style="width:{max_width}px; height:{max_height}px; '
                f'object-fit:cover; border-radius:4px; border:2px solid {img.get("border", "#ddd")};" '
                f'title="{img.get("title", "")}" />'
                f'<span style="position:absolute; top:4px; left:4px; '
                f'background:white; padding:2px 6px; border-radius:3px; '
                f'font-size:10px; font-weight:bold;">{img.get("badge", f"#{idx + 1}")}</span>'
                f'</div>'
            )

        html_parts.append('</div>')
        return mark_safe(''.join(html_parts))

    @staticmethod
    def stat_item(icon, label, value, color="#666"):
        return format_html(
            '<div style="font-size:12px; line-height:1.6;">'
            '<span style="color:{};">{} {}: <strong>{}</strong></span>'
            '</div>',
            color, icon, label, value
        )

    @staticmethod
    def alert(message, level="info"):
        levels = {
            "info": ("#e3f2fd", "#1976d2"),
            "success": ("#e8f5e9", "#2e7d32"),
            "warning": ("#fff3e0", "#f57c00"),
            "error": ("#ffebee", "#c62828"),
        }
        bg, text_color = levels.get(level, levels["info"])
        return format_html(
            '<div style="background:{}; color:{}; padding:12px 15px; '
            'border-radius:6px; font-size:12px; border-left:4px solid {};">'
            '{}'
            '</div>',
            bg, text_color, text_color, message
        )


class AdminLink:
    """Generate admin links and URLs"""

    @staticmethod
    def button(text, href, style="primary", target="_blank"):
        styles = {
            "primary": ("background:#417690; color:white;", "🔗"),
            "success": ("background:#2e7d32; color:white;", "✅"),
            "warning": ("background:#f57c00; color:white;", "⚠️"),
            "danger": ("background:#c62828; color:white;", "❌"),
        }
        base_style, icon = styles.get(style, styles["primary"])

        return format_html(
            '<a href="{}" target="{}" style="{}padding:10px 16px; '
            'border-radius:6px; text-decoration:none; font-weight:bold; '
            'display:inline-block;">{} {}</a>',
            href, target, base_style, icon, text
        )

    @staticmethod
    def external_link(text, href, icon="🔗"):
        return format_html(
            '<a href="{}" target="_blank" style="color:#417690; text-decoration:none;">'
            '{} {}</a>',
            href, icon, text
        )


class AdminTable:
    """Generate HTML tables for admin"""

    @staticmethod
    def simple(rows, columns, alternating=True):
        html = ['<table style="width:100%; border-collapse:collapse;">']

        for idx, row in enumerate(rows):
            bg = "#f8f9fa" if alternating and idx % 2 == 0 else "white"
            html.append(f'<tr style="background:{bg}; border-bottom:1px solid #ddd;">')

            for cell in row:
                html.append(f'<td style="padding:8px 12px; font-size:12px;">{cell}</td>')

            html.append('</tr>')

        html.append('</table>')
        return mark_safe(''.join(html))
