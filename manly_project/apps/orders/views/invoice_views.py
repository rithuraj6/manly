from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.orders.models import Order


@login_required
def print_invoice(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    items = order.items.select_related("product")

    context = {
        "order": order,
        "items": items,
        "print_mode": True,  # used in template
    }

    return render(request, "orders/invoice_print.html", context)


@login_required
def order_invoice(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    items = order.items.filter(
        status__in=["delivered", "returned"]
    ).select_related("product")

    context = {
        "order": order,
        "items": items,
    }

    return render(request, "orders/invoice.html", context)