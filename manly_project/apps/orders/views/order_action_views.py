from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


from apps.orders.models import OrderItem
from apps.orders.utils.stock import restore_stock


@login_required
def cancel_order_item(request, item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

   
    if order_item.status not in ["cancelled", "returned"]:
        restore_stock(order_item)
        order_item.status = "cancelled"
        order_item.save(update_fields=["status"])

        messages.success(request, "Item cancelled and stock restored")

    return redirect("order_detail", order_item.order.order_id)

