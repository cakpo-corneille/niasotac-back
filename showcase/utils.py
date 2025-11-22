import urllib.parse
from datetime import datetime
from decimal import Decimal
import locale
import pytz
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.text import slugify


def format_price(price, with_decimals=False, display_mode=True, use_locale=False):
    """
    Formate un prix en FCFA avec gestion des cas None et gratuité.

    :param price: Decimal, float ou int représentant le prix
    :param with_decimals: bool, True pour afficher 2 décimales
    :param display_mode: bool, True pour affichage utilisateur ("—" si None),
                         False pour logique interne ("0 FCFA" si None)
    :param use_locale: bool, True pour utiliser la locale française si disponible
    :return: str formaté, ex: "1 999 FCFA" ou "1 999,50 FCFA"
    """
    # Gestion du cas None
    if price is None:
        return "—" if display_mode else "0 FCFA"

    try:
        if use_locale:
            try:
                locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
            except locale.Error:
                use_locale = False

        if with_decimals:
            if use_locale:
                formatted = locale.format_string('%.2f', float(price), grouping=True)
            else:
                formatted = f"{float(price):,.2f}".replace(',', ' ')
        else:
            if use_locale:
                formatted = locale.format_string('%d', int(round(price)), grouping=True)
            else:
                formatted = f"{int(round(price)):,}".replace(',', ' ')
        
        return f"{formatted} FCFA"
    except Exception:
        return str(price) + " FCFA"

def generate_unique_slug(model_class, base_text, max_length=180, slug_field='slug'):
    base_slug = slugify(base_text)[:max_length-10]
    slug = base_slug
    counter = 1

    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug

def generate_sku(category_slug, model_class, prefix_length=3):
    prefix = category_slug[:prefix_length].upper() if category_slug else "PRD"

    last_product = model_class.objects.filter(
        sku__startswith=prefix
    ).order_by('-sku').first()

    if last_product and last_product.sku:
        try:
            last_num = int(last_product.sku.split('-')[-1])
            new_num = last_num + 1
        except (ValueError, IndexError):
            new_num = 1
    else:
        new_num = 1

    return f"{prefix}-{new_num:05d}"

def build_whatsapp_message(product, settings_obj):
    benin_tz = pytz.timezone("Africa/Porto-Novo")
    current_hour = datetime.now(benin_tz).hour
    salutation = "Bonsoir" if current_hour >= 12 else "Bonjour"

    message_parts = [
        f"{salutation} {settings_obj.company_name},",
        "",
        "Je suis intéressé(e) par le produit suivant:",
        "",
    ]

    if product.name:
        message_parts.append(f"📱 *{product.name}*")

    if product.brand:
        message_parts.append(f"🏷️ Marque: {product.brand}")

    if product.price:
        message_parts.append(f"💰 Prix: {format_price(product.price)}")

    if hasattr(product, 'has_discount') and product.has_discount:
        message_parts.append(f"🎉 Réduction: -{product.discount_percent}%")

    try:
        product_url = build_absolute_url(product.get_absolute_url())
        message_parts.append(f"🖼️ Voir le produit: {product_url}")
    except Exception:
        pass

    message_parts.append("")
    message_parts.append("Merci de me contacter pour plus d'informations.")

    return "\n".join(message_parts)

def build_absolute_url(relative_url, request=None):
    if request:
        return request.build_absolute_uri(relative_url)

    try:
        current_site = Site.objects.get_current()
        return f"https://{current_site.domain}{relative_url}"
    except Exception:
        frontend_url = getattr(settings, "FRONTEND_URL", None)
        if frontend_url:
            return f"{frontend_url}{relative_url}"
        return f"https://localhost{relative_url}"

def build_whatsapp_link(phone_number, message):
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/{phone_number}?text={encoded_message}"
