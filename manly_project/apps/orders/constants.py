from decimal import Decimal

MAX_QTY_PER_ITEM = 10   

ORDER_STATUS_FLOW = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["out_for_delivery", "cancelled"],
    "out_for_delivery": ["delivered"],
    "delivered": [],
    "cancelled": [],
    "partially_refunded": ["shipped"],

}




class RefundEvent:
    
    USER_CANCEL = "user_cancel"
    ADMIN_CANCEL = "admin_cancel"
    RETURN_APPROVED = "return_approved"
    
    
    
    