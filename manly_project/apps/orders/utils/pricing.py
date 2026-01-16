from decimal import Decimal
from apps.cart.models import Cart

from decimal import Decimal, ROUND_HALF_UP



def distribute_amount(total_amount, items):
    if not items:
        return []

    total_base = sum(item["base"] for item in items)

    if total_base == 0:
        return [Decimal("0.00")] * len(items)

    distributed = []
    running_total = Decimal("0.00")

    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = total_amount - running_total
        else:
            share = (
                (item["base"] / total_base) * total_amount
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            running_total += share

        distributed.append(share)

    return distributed





def calculate_grand_total(user):


    cart = Cart.objects.select_related().get(user=user)

    subtotal = Decimal("0.00")

    for item in cart.items.select_related("product"):
        subtotal += item.product.base_price * item.quantity

    delivery_fee = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + delivery_fee) * Decimal("0.18")).quantize(Decimal("0.01"))

    total_amount = subtotal + delivery_fee + tax
    return total_amount