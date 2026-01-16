from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderItem
from apps.orders.utils.pricing import distribute_amount
from apps.orders.utils.pricing import apply_offer

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from apps.orders.models import Order, OrderItem
from apps.orders.utils.pricing import distribute_amount
from apps.orders.utils.pricing import apply_offer

@transaction.atomic
def create_order(
    *,
    user,
    cart,
    address_snapshot,
    payment_method,
    is_paid
):
    cart_items = cart.items.select_related(
        "product", "variant", "product__category"
    )

    items_data = []
    subtotal = Decimal("0.00")

   
    for item in cart_items:
        base = item.product.base_price * item.quantity
        subtotal += base
        items_data.append({"base": base})

  
    delivery_fee = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + delivery_fee) * Decimal("0.18")).quantize(Decimal("0.01"))
    total_amount = subtotal + delivery_fee + tax

    
    month_code = timezone.now().strftime("%b").upper()
    count = Order.objects.filter(
        created_at__month=timezone.now().month
    ).count() + 1
    order_id = f"ORD-MAN-{month_code}-{count:03d}"

  
    order = Order.objects.create(
        user=user,
        order_id=order_id,
        payment_method=payment_method,
        is_paid=is_paid,
        subtotal=subtotal,
        shipping_charge=delivery_fee,
        tax=tax,
        total_amount=total_amount,
        address_snapshot=address_snapshot,
    )

   
    tax_shares = distribute_amount(tax, items_data)
    delivery_shares = distribute_amount(delivery_fee, items_data)

    for index, item in enumerate(cart_items):
        base = item.product.base_price * item.quantity
        item_tax = tax_shares[index]
        item_shipping = delivery_shares[index]

        final_price_paid = base + item_tax + item_shipping

        if final_price_paid is None:
            raise ValueError("final_price_paid is None – pricing bug")

        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            price=item.product.base_price,
            line_total=base,
            final_price_paid=final_price_paid,
            status=OrderItem.STATUS_PENDING,
        )

        item.variant.stock -= item.quantity
        item.variant.save(update_fields=["stock"])

   
    cart.items.all().delete()

    return order