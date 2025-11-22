from celery import shared_task
from showcase.models import ProductStatus
from showcase.services.scoring_service import ScoringService

@shared_task
def recalculate_product_scores(product_status_id):
    try:
        instance = ProductStatus.objects.get(pk=product_status_id)
        is_featured, featured_score = ScoringService.calculate_featured_score(instance)
        is_recommended, recommendation_score = ScoringService.calculate_recommendation_score(instance)

        update_needed = (
            instance.is_featured != is_featured or
            instance.featured_score != featured_score or
            instance.is_recommended != is_recommended or
            instance.recommendation_score != recommendation_score
        )

        if update_needed:
            instance.is_featured = is_featured
            instance.featured_score = featured_score
            instance.is_recommended = is_recommended
            instance.recommendation_score = recommendation_score
            instance.save(update_fields=[
                'is_featured',
                'featured_score',
                'is_recommended',
                'recommendation_score'
            ])
    except ProductStatus.DoesNotExist:
        pass
