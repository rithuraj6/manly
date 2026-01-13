from decimal import Decimal
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from django.db import transaction
from django.utils import timezone

from apps.cart.models import Cart
from apps.accounts.models import UserAddress
from apps.orders.models import Order, OrderItem
from apps.orders.utils.pricing import distribute_amount
from apps.orders.services.order_creation import create_order


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

    order = create_order(
        user=user,
        cart=cart,
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
        payment_method="cod",
        is_paid=False
    )

    return redirect("order_success", order_id=order.order_id)