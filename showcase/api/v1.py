"""
API v1 - Routes principales de l'API
"""
from rest_framework import routers
from showcase.views import (
    CategoryViewSet, ProductViewSet, PromotionViewSet,
    NewsletterSubscriberViewSet, NewsletterTemplateViewSet, 
    NewsletterCampaignViewSet, ServiceViewSet, SocialLinkViewSet,
    SiteSettingsViewSet
)

# Create router and register viewsets
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'promotions', PromotionViewSet, basename='promotion')
router.register(r'newsletter/subscribers', NewsletterSubscriberViewSet, basename='newsletter-subscriber')
router.register(r'newsletter/templates', NewsletterTemplateViewSet, basename='newsletter-template')
router.register(r'newsletter/campaigns', NewsletterCampaignViewSet, basename='newsletter-campaign')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'social-links', SocialLinkViewSet, basename='social-link')
router.register(r'settings', SiteSettingsViewSet, basename='settings')

urlpatterns = router.urls
