from datetime import timedelta
from decimal import Decimal
from django.db.models import Avg
from django.utils import timezone

from ..constants import (
    SCORE_WEIGHTS,
    RECOMMENDATION_WEIGHTS,
    FEATURED_SCORE_THRESHOLD,
    RECOMMENDATION_SCORE_THRESHOLD
)


class ScoringService:

    @staticmethod
    def calculate_featured_score(product_status):
        product = product_status.product

        if product_status.exclude_from_featured:
            return False, Decimal('0.0')

        if product_status.force_featured:
            return True, Decimal('100.0')

        score = Decimal('0.0')

        views_last_30_days = product_status.get_views_last_n_days(30)
        score += min(views_last_30_days / 100 * SCORE_WEIGHTS['views'], SCORE_WEIGHTS['views'])

        score += min(
            product_status.whatsapp_click_count / 50 * SCORE_WEIGHTS['whatsapp_clicks'],
            SCORE_WEIGHTS['whatsapp_clicks']
        )

        days_since_creation = (timezone.now() - product.created_at).days
        if days_since_creation <= 7:
            novelty_score = 10
        elif days_since_creation <= 30:
            novelty_score = 7
        elif days_since_creation <= 90:
            novelty_score = 5
        else:
            novelty_score = 2
        score += novelty_score

        if product.stock_quantity >= 20:
            stock_score = 15
        elif product.stock_quantity >= 10:
            stock_score = 10
        elif product.stock_quantity > 0:
            stock_score = 5
        else:
            stock_score = 0
        score += stock_score

        avg_price = product.category.products.filter(
            is_active=True, in_stock=True
        ).aggregate(avg=Avg('price'))['avg'] or product.price

        if product.price <= avg_price * Decimal('0.8'):
            price_score = 10
        elif product.price <= avg_price:
            price_score = 7
        else:
            price_score = 3
        score += price_score

        if product.cost_price and product.cost_price > 0:
            margin = ((product.price - product.cost_price) / product.price) * 100
            if margin >= 40:
                margin_score = 10
            elif margin >= 25:
                margin_score = 7
            elif margin >= 15:
                margin_score = 4
            else:
                margin_score = 0
            score += margin_score
        else:
            score += 5

        final_score = round(score, 2)
        is_featured = final_score >= FEATURED_SCORE_THRESHOLD

        return is_featured, final_score

    @staticmethod
    def calculate_recommendation_score(product_status):
        product = product_status.product

        if product_status.exclude_from_recommended:
            return False, Decimal('0.0')

        if product_status.force_recommended:
            return True, Decimal('100.0')

        score = Decimal('0.0')

        total_engagement = product_status.view_count + (product_status.whatsapp_click_count * 3)
        score += min(
            total_engagement / 200 * RECOMMENDATION_WEIGHTS['engagement'],
            RECOMMENDATION_WEIGHTS['engagement']
        )

        if product.stock_quantity > 0:
            if product_status.view_count > 0:
                demand_ratio = product_status.view_count / max(product.stock_quantity, 1)
                if demand_ratio >= 5:
                    score += 20
                elif demand_ratio >= 2:
                    score += 15
                else:
                    score += 10
            else:
                score += 5

        category_products = product.category.products.filter(is_active=True)
        if category_products.exists():
            products_above = category_products.filter(
                status__view_count__gt=product_status.view_count
            ).count()
            total_products = category_products.count()
            percentile = (1 - products_above / max(total_products, 1)) * 100

            if percentile >= 80:
                score += 20
            elif percentile >= 50:
                score += 15
            elif percentile >= 30:
                score += 10
            else:
                score += 5
        else:
            score += 10

        if product.compare_at_price and product.compare_at_price > product.price:
            discount_percent = (
                (product.compare_at_price - product.price) / product.compare_at_price * 100
            )
            if discount_percent >= 30:
                score += 15
            elif discount_percent >= 15:
                score += 12
            else:
                score += 8
        else:
            score += 7

        if product_status.last_viewed_at:
            days_since_view = (timezone.now() - product_status.last_viewed_at).days
            if days_since_view <= 7:
                score += 10
            elif days_since_view <= 30:
                score += 7
            elif days_since_view <= 90:
                score += 4
        else:
            score += 5

        final_score = round(score, 2)
        is_recommended = final_score >= RECOMMENDATION_SCORE_THRESHOLD

        return is_recommended, final_score
