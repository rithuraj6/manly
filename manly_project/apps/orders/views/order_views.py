from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from apps.cart.models import Cart
from apps.accounts.models import UserAddress
from apps.orders.models import Order, OrderItem
from apps.orders.utils.pricing import distribute_amount


@login_required
@transaction.atomic
def place_order(request):

    if request.method != "POST":
        return redirect("checkout_page")

    user = request.user
    cart = getattr(user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    address_id = request.session.get("checkout_address_id")
    if not address_id:
        return redirect("checkout_page")

    address = get_object_or_404(UserAddress, id=address_id, user=user)
    del request.session["checkout_address_id"]

    cart_items = cart.items.select_related("product", "variant", "product__category")


    for item in cart_items:
        product = item.product
        variant = item.variant

        if (
            not product.is_active or
            not product.category.is_active or
            not variant.is_active or
            variant.stock < item.quantity
        ):
            return redirect("cart_page")

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
    count = Order.objects.filter(created_at__month=timezone.now().month).count() + 1
    order_id = f"ORD-MAN-{month_code}-{count:03d}"

    order = Order.objects.create(
        user=user,
        order_id=order_id,

        subtotal=subtotal,
        shipping_charge=delivery_fee,
        tax=tax,
        total_amount=total_amount,

        payment_method="cod",
        is_paid=False,

        address_snapshot={
            "full_name": address.full_name,
            "phone": address.phone,
            "house_name": address.house_name,
            "street": address.street,
            "land_mark": address.land_mark,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "pincode": address.pincode,
        },
    )

  
  
    tax_shares = distribute_amount(tax, items_data)
    delivery_shares = distribute_amount(delivery_fee, items_data)



    for index, item in enumerate(cart_items):
        base = item.product.base_price * item.quantity
        item_tax = tax_shares[index]
        item_shipping = delivery_shares[index]

        final_price_paid = base + item_tax + item_shipping
        
        if final_price_paid is None:
            raise ValueError('final_price_paid is None - Pricing bug')

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

    return redirect("order_success", order_id=order.order_id)
