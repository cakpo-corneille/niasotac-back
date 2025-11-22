from decimal import Decimal
from django.utils import timezone
from django.db.models import F


class PromotionService:

    @staticmethod
    def get_applicable_promotions(product):
        from ..models import Promotion

        now_qs = Promotion.objects.filter(active=True)
        applicable = [p for p in now_qs if p.is_active_now() and p.applies_to_product(product)]
        return applicable

    @staticmethod
    def get_best_promotion(product, quantity=1):
        promos = PromotionService.get_applicable_promotions(product)
        best = None
        best_final = product.price

        for promo in promos:
            disc, final_unit = promo.get_discount_amount(product, quantity=1)
            if final_unit < best_final:
                best_final = final_unit
                best = (promo, disc, final_unit)

        return best

    @staticmethod
    def calculate_price_with_promotions(product, quantity=1):
        qty = max(1, int(quantity))
        original = product.price
        applicable = PromotionService.get_applicable_promotions(product)

        if not applicable:
            return Decimal('0.00'), original

        stackable = [p for p in applicable if p.is_stackable]
        non_stackable = [p for p in applicable if not p.is_stackable]

        unit_price_stack = original

        set_prices = [
            p.value for p in stackable
            if p.promotion_type == 'set_price' and p.value is not None
        ]
        if set_prices:
            try:
                unit_price_stack = min([Decimal(v) for v in set_prices])
            except Exception:
                pass

        amount_total = Decimal('0.00')
        for p in stackable:
            if p.promotion_type == 'amount' and p.value:
                try:
                    amount_total += Decimal(p.value)
                except Exception:
                    pass
        unit_price_stack = max(Decimal('0.00'), unit_price_stack - amount_total)

        percent_values = [
            Decimal(p.value) for p in stackable
            if p.promotion_type == 'percent' and p.value is not None
        ]
        for pct in percent_values:
            try:
                unit_price_stack = (
                    unit_price_stack * (Decimal('1') - (pct / Decimal('100')))
                ).quantize(Decimal('0.01'))
            except Exception:
                pass

        final_unit_stack = unit_price_stack.quantize(Decimal('0.01'))

        best_non_stack_final = original
        for p in non_stackable:
            try:
                _, final = p.get_discount_amount(product, quantity=1)
                if final < best_non_stack_final:
                    best_non_stack_final = final
            except Exception:
                continue

        candidate_unit = min(final_unit_stack, best_non_stack_final)
        if candidate_unit is None:
            candidate_unit = original

        candidate_unit = Decimal(candidate_unit).quantize(Decimal('0.01'))
        total_discount = (original - candidate_unit) * qty

        return total_discount.quantize(Decimal('0.01')), candidate_unit

    @staticmethod
    def redeem_promotion(promotion, user=None, increment=1):
        from ..models import PromotionUsage

        if promotion.usage_limit is not None and (promotion.usage_count() + increment) > promotion.usage_limit:
            return False

        if user and promotion.per_user_limit is not None:
            usage, _ = PromotionUsage.objects.get_or_create(promotion=promotion, user=user)
            if (usage.count + increment) > promotion.per_user_limit:
                return False
            usage.count = F('count') + increment
            usage.last_used_at = timezone.now()
            usage.save(update_fields=['count', 'last_used_at'])
            usage.refresh_from_db()
            return True

        if not user:
            usage, _ = PromotionUsage.objects.get_or_create(promotion=promotion, user=None)
            usage.count = F('count') + increment
            usage.last_used_at = timezone.now()
            usage.save(update_fields=['count', 'last_used_at'])
            usage.refresh_from_db()
            return True

        return True
