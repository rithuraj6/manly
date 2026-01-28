from django.shortcuts import redirect, get_object_or_404
from apps.accounts.decorators import user_required
from django.db import transaction

from apps.cart.models import Cart

from apps.orders.services.order_creation import create_order


@user_required
@transaction.atomic
def place_order(request):
    
    user = request.user
    cart = getattr(user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    address_snapshot = request.session.get("checkout_address_snapshot")
    if not address_snapshot:
        messages.error(request, "Address missing. Please checkout again.")
        return redirect("checkout_page")

  

    order = create_order(
        user=user,
        cart=cart,
        address_snapshot=address_snapshot,
        payment_method="cod",
        is_paid=False
    )

    return redirect("order_success", order_id=order.order_id)