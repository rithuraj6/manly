from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.decorators import user_required
from apps.orders.models import Order

@user_required
def print_invoice(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related("user", "payment"),
        order_id=order_id,
        user=request.user
    )
    items = order.items.all()

    context = {
        "order": order,
        "items": items,
        "print_mode": True,
    }

    return render(request, "orders/invoice.html", context)


@user_required
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

    return render(request, "orders/invoice_print.html", context)