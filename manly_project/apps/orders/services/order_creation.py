

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderItem
from apps.orders.utils.pricing import distribute_amount
from apps.orders.utils.pricing import apply_offer
from apps.orders.constants import MAX_QTY_PER_ITEM


from apps.coupons.models import Coupon, CouponUsage
from apps.coupons.utils.pricing import calculate_coupon_discount



@transaction.atomic
def create_order(
    *,
    user,
    cart,
    address_snapshot,
    payment_method,
    is_paid,
    coupon_id=None,  
):
    cart_items = cart.items.select_related(
        "product", "variant", "product__category"
    )

    items_data = []
    discounted_prices = []
    subtotal = Decimal("0.00")

  
    for item in cart_items:
        if item.quantity <= 0:
            raise ValueError("Invalid item quantity")

        if item.quantity > MAX_QTY_PER_ITEM:
            raise ValueError("Quantity exceeds allowed limit")

        if item.quantity > item.variant.stock:
            raise ValueError("Insufficient stock during order creation")

        discounted_price = apply_offer(
            item.product,
            item.product.base_price
        )

        line_total = discounted_price * item.quantity
        subtotal += line_total

        discounted_prices.append(discounted_price)
        items_data.append({"base": line_total})



    coupon = None
    coupon_discount = Decimal("0.00")

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)

          
            coupon_discount = calculate_coupon_discount(
                coupon=coupon,
                subtotal=subtotal
            )

            if coupon_discount <= 0:
                coupon = None
                coupon_id = None

            else:
                if CouponUsage.objects.filter(
                    user=user, coupon=coupon
                ).exists():
                    raise ValueError("Coupon already used")

        except Coupon.DoesNotExist:
            coupon = None
            coupon_id = None

 
    adjusted_subtotal = subtotal - coupon_discount
    if adjusted_subtotal < 0:
        adjusted_subtotal = Decimal("0.00")


    delivery_fee = Decimal("0.00") if adjusted_subtotal >= 3000 else Decimal("150.00")

    tax = (adjusted_subtotal * Decimal("0.18")).quantize(
    Decimal("0.01")
    )

    total_amount = adjusted_subtotal + delivery_fee + tax

 
    month_code = timezone.now().strftime("%b").upper()
    count = Order.objects.filter(
        created_at__month=timezone.now().month
    ).count() + 1

    order = Order.objects.create(
        user=user,
        order_id=f"ORD-MAN-{month_code}-{count:03d}",
        payment_method=payment_method,
        is_paid=is_paid,
        subtotal=subtotal,
        coupon=coupon,
        coupon_discount=coupon_discount,
        shipping_charge=delivery_fee,
        tax=tax,
        total_amount=total_amount,
        address_snapshot=address_snapshot,
    )

  
    coupon_shares = distribute_amount(coupon_discount, items_data)
    tax_shares = distribute_amount(tax, items_data)
    delivery_shares = distribute_amount(delivery_fee, items_data)

    for index, item in enumerate(cart_items):
        base = discounted_prices[index] * item.quantity

        final_price_paid = max(
            Decimal("0.00"),
            base - coupon_shares[index]
        ) + tax_shares[index] + delivery_shares[index]

        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            price=discounted_prices[index],
            line_total=base,
            final_price_paid=final_price_paid,
            status=OrderItem.STATUS_PENDING,
        )

       
        item.variant.stock -= item.quantity
        item.variant.save(update_fields=["stock"])


    if coupon:
        CouponUsage.objects.get_or_create(
            user=user,
            coupon=coupon
        )

    
    cart.items.all().delete()

    return order