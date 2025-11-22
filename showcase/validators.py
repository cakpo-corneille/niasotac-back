from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from decimal import Decimal

def validate_image_size(image, max_size_mb=5):
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"La taille de l'image ne doit pas dépasser {max_size_mb}MB.")

def validate_product_image_size(image):
    validate_image_size(image, max_size_mb=5)
    width, height = get_image_dimensions(image)
    if width < 300 or height < 300:
        raise ValidationError("Les dimensions minimales sont 300x300 pixels.")

def validate_promotion_dates(start_at, end_at):
    if start_at and end_at and start_at > end_at:
        raise ValidationError("La date de début doit être antérieure à la date de fin.")

def validate_promotion_value(promotion_type, value, buy_x=None, get_y=None):
    if promotion_type == 'percent' and value is not None:
        if value < 0 or value > 100:
            raise ValidationError("Le pourcentage doit être entre 0 et 100.")

    if promotion_type in ['amount', 'set_price'] and (value is None or value <= Decimal('0.0')):
        raise ValidationError("La valeur doit être positive pour ce type de promotion.")

    if promotion_type == 'bogo':
        if not buy_x or buy_x <= 0 or not get_y or get_y <= 0:
            raise ValidationError("Pour BOGO, buy_x et get_y doivent être des entiers positifs.")
