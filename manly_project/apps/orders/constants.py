ORDER_STATUS_FLOW = {
    "pending": ["shipped", "cancelled"],
    "shipped": ["out_for_delivery", "cancelled"],
    "out_for_delivery": ["delivered"],
    "delivered": [],
    "cancelled": [],
    "partially_refunded": ["shipped"],
}