from django.contrib.admin import site

from .category_admin import CategoryAdmin
from .product_admin import ProductAdmin, ProductImageAdmin
from .promotion_admin import PromotionAdmin
from .newsletter_admin import (
    NewsletterSubscriberAdmin,
    NewsletterTemplateAdmin,
    NewsletterCampaignAdmin,
    NewsletterLogAdmin,
)
from .settings_admin import SiteSettingsAdmin, SocialLinkAdmin, ServiceAdmin


site.site_header = "NIASOTAC TECHNOLOGIE - Administration"
site.site_title = "NIASOTAC Admin"
site.index_title = "Tableau de bord de gestion"

__all__ = [
    'CategoryAdmin',
    'ProductAdmin',
    'ProductImageAdmin',
    'PromotionAdmin',
    'NewsletterSubscriberAdmin',
    'NewsletterTemplateAdmin',
    'NewsletterCampaignAdmin',
    'NewsletterLogAdmin',
    'SiteSettingsAdmin',
    'SocialLinkAdmin',
    'ServiceAdmin',
    
]
