from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.orders.models import OrderItem

@login_required
def cancel_order_item(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status__in=["pending", "confirmed"]
    )

    item.status = "cancelled"
    item.save()

    return redirect("order_detail", order_id=item.order.order_id)
