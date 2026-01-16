from django.contrib.auth.decorators import login_required

from django.shortcuts import render, get_object_or_404
from apps.orders.models import Order


@login_required
def order_success(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    return render(request, "orders/order_success.html", {
        "order": order
    })