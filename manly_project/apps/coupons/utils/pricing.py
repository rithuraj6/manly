
from decimal import Decimal
from django.utils import timezone

def calculate_coupon_discount(*, coupon, subtotal):
    if not coupon or not coupon.is_active:
        return Decimal("0.00")

    today = timezone.now().date()


    if coupon.valid_from > today or coupon.valid_to < today:
        return Decimal("0.00")

    if subtotal < coupon.min_purchase_amount:
        return Decimal("0.00")

    discount = Decimal("0.00")

    if coupon.discount_type == "PERCENT":
        discount = (subtotal * coupon.discount_value / Decimal("100")).quantize(
            Decimal("0.01")
        )

        if coupon.max_discount_amount:
            discount = min(discount, coupon.max_discount_amount)

    elif coupon.discount_type == "FLAT":
        discount = coupon.discount_value

    if discount > subtotal:
        discount = subtotal

    return discount
