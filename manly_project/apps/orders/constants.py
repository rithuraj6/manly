ORDER_STATUS_FLOW = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["out_for_delivery"],
    "out_for_delivery": ["delivered"],
    "delivered": [],  
    "cancelled": [],
    "returned": [],
    "refunded": [],
}
