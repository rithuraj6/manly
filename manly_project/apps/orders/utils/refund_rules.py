def should_refund_wallet(order):
    
    if order.payment_method in ("razorpay","wallet"):
        return True
    
    if order.payment_method == 'cod' and order.status in(
        "delivered","partially_refund","returned"
    ):
        return True
    return False