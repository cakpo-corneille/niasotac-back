from decimal import Decimal

FEATURED_SCORE_THRESHOLD = Decimal('70.0')
RECOMMENDATION_SCORE_THRESHOLD = Decimal('65.0')

MAX_IMAGES_PER_PRODUCT = 10
NEW_PRODUCT_DAYS_THRESHOLD = 30

SCORE_WEIGHTS = {
    'views': Decimal('30.0'),
    'whatsapp_clicks': Decimal('25.0'),
    'novelty': Decimal('10.0'),
    'stock': Decimal('15.0'),
    'price': Decimal('10.0'),
    'margin': Decimal('10.0'),
}

RECOMMENDATION_WEIGHTS = {
    'engagement': Decimal('35.0'),
    'stock_demand': Decimal('20.0'),
    'category_popularity': Decimal('20.0'),
    'price_attractiveness': Decimal('15.0'),
    'recency': Decimal('10.0'),
}

PRODUCT_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'webp']
ICON_FORMATS = ['ico', 'png', 'jpg', 'jpeg', 'svg', 'webp']

SOCIAL_MEDIA_PLATFORMS = [
    ("Facebook", "Facebook"),
    ("Twitter", "Twitter"),
    ("Instagram", "Instagram"),
    ("Linkedin", "Linkedin"),
    ("Youtube", "Youtube"),
]

PROMOTION_TYPES = [
    ("percent", "Pourcentage"),
    ("amount", "Montant fixe"),
    ("set_price", "Prix fixé"),
    ("bogo", "Buy X Get Y"),
]

NEWSLETTER_CAMPAIGN_STATUSES = [
    ('draft', "Brouillon"),
    ('scheduled', "Planifiée"),
    ('sending', "Envoi"),
    ('sent', "Envoyée"),
    ('cancelled', "Annulée"),
]
