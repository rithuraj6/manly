from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from apps.wallet.services.wallet_services import refund_to_wallet
from apps.orders.services.order_state import recalculate_order_status

from django.db import transaction
from apps.orders.models import OrderItem
from apps.orders.utils.stock import restore_stock

@transaction.atomic
@login_required
def cancel_order_item(request, item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status=OrderItem.STATUS_PENDING
    )

    order = order_item.order

 
    order_item.status = OrderItem.STATUS_CANCELLED
    order_item.save(update_fields=["status"])

   
    restore_stock(order_item)

    refund_to_wallet(
        user=order.user,
        amount=order_item.final_price_paid,
        reason=f"Refund for cancelled item {order_item.product.name}",
        order=order,
    )

    recalculate_order_status(order)

    messages.success(request, "Item cancelled & refund credited to wallet")
    return redirect("order_detail", order_id=order.order_id)
