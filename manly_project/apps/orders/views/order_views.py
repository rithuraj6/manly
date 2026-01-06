from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart
from apps.accounts.models import UserAddress


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

    subtotal = Decimal("0.00")

    for item in cart.items.select_related("product", "variant", "product__category"):
        product = item.product
        variant = item.variant

        if (
            not product.is_active or
            not product.category.is_active or
            not variant.is_active or
            variant.stock < item.quantity
        ):
            return redirect("cart_page")

        subtotal += product.base_price * item.quantity

    shipping = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + shipping) * Decimal("0.18")).quantize(Decimal("0.01"))
    total = subtotal + shipping + tax

    month_code = timezone.now().strftime("%b").upper()
    count = Order.objects.filter(created_at__month=timezone.now().month).count() + 1
    order_id = f"ORD-MAN-{month_code}-{count:03d}"

    order = Order.objects.create(
        user=user,
        order_id=order_id,
        subtotal=subtotal,
        tax=tax,
        shipping_charge=shipping,
        total_amount=total,
        payment_method="cod",
        is_paid=False,
        address_snapshot = {
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

    for item in cart.items.select_related("product", "variant"):
        OrderItem.objects.create(
            order=order,
            product=item.product,
            variant=item.variant,
            quantity=item.quantity,
            price=item.product.base_price,
            line_total=item.product.base_price * item.quantity,
        )

        item.variant.stock -= item.quantity
        item.variant.save()

    cart.items.all().delete()

    return redirect("order_success", order_id=order.order_id)
