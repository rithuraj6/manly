
from apps.cart.models import Cart

from decimal import Decimal, ROUND_HALF_UP
from apps.offers.models import Offer

from django.utils import timezone

from decimal import Decimal
from apps.offers.models import Offer


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



def get_best_offer(product):
  
    now = timezone.now()

    product_offer = Offer.objects.filter(
        product=product,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).first()

    category_offer = Offer.objects.filter(
        category=product.category,
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).first()

    if not product_offer and not category_offer:
        return None

    if product_offer and category_offer:
        return (
            product_offer
            if product_offer.discount_percentage >= category_offer.discount_percentage
            else category_offer
        )

    return product_offer or category_offer







def get_product_offer(product):
    return (
        Offer.objects.filter(
            product=product,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        )
        .order_by("-discount_percentage")
        .values_list("discount_percentage", flat=True)
        .first()
    )


def get_category_offer(category):
    return (
        Offer.objects.filter(
            category=category,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        )
        .order_by("-discount_percentage")
        .values_list("discount_percentage", flat=True)
        .first()
    )


def apply_offer(product, base_price):
    product_offer = get_product_offer(product)
    category_offer = get_category_offer(product.category)

    offers = [o for o in (product_offer, category_offer) if o]

    if not offers:
        return base_price

    best_offer = max(offers)  

    discount_amount = (Decimal(best_offer) / Decimal("100")) * base_price
    return (base_price - discount_amount).quantize(Decimal("0.01"))