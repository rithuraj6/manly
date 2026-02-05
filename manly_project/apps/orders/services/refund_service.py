from decimal import Decimal
from django.db import transaction

from apps.orders.constants import RefundEvent

from apps.wallet.services.wallet_services import refund_to_wallet

@transaction.atomic
def process_refund(*, order_item,event,initiated_by="system"):
    
    order = order_item.order
    payment_method = order.payment_method
    amount = order_item.final_price_paid or Decimal("0.00")
    
    if amount <= 0:
        
        return False
    
    if payment_method in ("razorpay" ,"wallet"):
        if event in(
            RefundEvent.USER_CANCEL,
            RefundEvent.ADMIN_CANCEL,
            RefundEvent.RETURN_APPROVED,
        ):
            
            refund_to_wallet(user=order.user,
                             order_item=order_item,
                             amount=amount,
                             reason=f"Refund ({event}) for order {order.order_id}",
            )
            
            return True
        return False
    
    
    if payment_method == "cod":
        
        if (event==RefundEvent.RETURN_APPROVED and order.is_paid):
            refund_to_wallet(
                user=order.user,
                order_item=order_item,
                amount=amount,
                reason=f"COD return refund for order {order.order_id}"
            )
            
            return True
        
       
    
        return False

