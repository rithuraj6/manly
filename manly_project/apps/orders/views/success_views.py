from apps.accounts.decorators import user_required

from django.shortcuts import render, get_object_or_404
from apps.orders.models import Order


@user_required
def order_success(request, order_uuid):
    order = get_object_or_404(
        Order,
        uuid=order_uuid,
        user=request.user
    )
    request.session.pop("checkout_address_snapshot", None)

    return render(request, "orders/order_success.html", {
        "order": order
    })