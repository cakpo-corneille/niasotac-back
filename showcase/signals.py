import os
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from showcase.models import ProductImage, Category, Product, ProductStatus
from showcase.services.scoring_service import ScoringService
from showcase.tasks import recalculate_product_scores


@receiver(pre_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    try:
        if instance.image:
            instance.image.delete(save=False)
    except Exception:
        pass

@receiver(pre_delete, sender=Category)
def delete_category_icon_file(sender, instance, **kwargs):
    try:
        if instance.icon_file:
            instance.icon_file.delete(save=False)
    except Exception:
        pass

@receiver(post_save, sender=Product)
def create_product_status(sender, instance, created, **kwargs):
    if created:
        ProductStatus.objects.get_or_create(product=instance)



@receiver(post_save, sender=ProductStatus)
def update_product_scores(sender, instance, created, **kwargs):
    if not created and not kwargs.get('update_fields'):
        # Déclenche la tâche Celery asynchrone
        recalculate_product_scores.delay(instance.id)

