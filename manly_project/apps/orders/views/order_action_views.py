from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from apps.orders.services.order_state import recalculate_order_status

from django.db import transaction
from apps.orders.models import OrderItem
from apps.orders.utils.stock import restore_stock


from apps.wallet.services.wallet_services import refund_to_wallet




@transaction.atomic
def cancel_order_item(request, item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status=OrderItem.STATUS_PENDING
    )

    refund_amount = order_item.final_price_paid

    
    order = order_item.order
    order_item.status = OrderItem.STATUS_CANCELLED
    order_item.save(update_fields=["status"])

   
    variant = order_item.variant
    variant.stock += order_item.quantity
    variant.save(update_fields=["stock"])
    
    restore_stock(order_item)

    
    if order.payment_method in ["razorpay", "wallet"]:
        refund_to_wallet(
            user=order.user,
            order_item=order_item,
            amount=order_item.final_price_paid,
            reason=f"Refund for cancelled item ({order.order_id})",
        )
        
    recalculate_order_status(order)

    messages.success(request, "Item cancelled and refund credited to wallet.")
    return redirect("order_detail", order_id=order_item.order.order_id)
