def recalculate_order_status(order):
    items = order.items.all()

    if items.filter(status="pending").exists():
        order.status = "pending"

    elif items.filter(status="shipped").exists():
        order.status = "shipped"

    elif items.filter(status="out_for_delivery").exists():
        order.status = "out_for_delivery"

    elif (
        items.filter(status="cancelled").exists() and
        items.exclude(status="cancelled").exists()
    ):
        order.status = "partially_refunded"

    elif items.filter(status="cancelled").count() == items.count():
        order.status = "cancelled"

    elif items.filter(status="delivered").count() == items.count():
        order.status = "delivered"

    order.save(update_fields=["status"])
