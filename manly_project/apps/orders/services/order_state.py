from decimal import Decimal
from django.db import models
from apps.orders.models import OrderItem


ACTIVE_STATUSES = [
    OrderItem.STATUS_PENDING,
    OrderItem.STATUS_CONFIRMED,
    OrderItem.STATUS_SHIPPED,
    OrderItem.STATUS_DELIVERED,
]

CANCELLED_STATUSES = [
    OrderItem.STATUS_CANCELLED,
]

RETURNED_STATUSES = [
    OrderItem.STATUS_RETURNED,
]



from decimal import Decimal
from django.db import models
from apps.orders.models import OrderItem


ACTIVE_STATUSES = [
    OrderItem.STATUS_PENDING,
    OrderItem.STATUS_CONFIRMED,
    OrderItem.STATUS_SHIPPED,
    OrderItem.STATUS_DELIVERED,
]

CANCELLED_STATUSES = [
    OrderItem.STATUS_CANCELLED,
]

RETURNED_STATUSES = [
    OrderItem.STATUS_RETURNED,
]



def recalculate_order_status(order):
    """
    Recalculate parent Order.status based on OrderItem statuses.
    This supports partial cancellation, partial refund, and shipping remaining items.
    """

    items = order.items.all()

    # If any item is pending → order is pending
    if items.filter(status="pending").exists():
        order.status = "pending"

    # If any item shipped → order shipped
    elif items.filter(status="shipped").exists():
        order.status = "shipped"

    # If any item out for delivery
    
    
    elif items.filter(status="out_for_delivery").exists():
        order.status = "out_for_delivery"

    # Partial cancel / refund case
    elif (
        items.filter(status="cancelled").exists()
        and items.exclude(status="cancelled").exists()
    ):
        order.status = "partially_refunded"

    # All cancelled
    elif items.filter(status="cancelled").count() == items.count():
        order.status = "cancelled"

    # All delivered
    elif items.filter(status="delivered").count() == items.count():
        order.status = "delivered"

    order.save(update_fields=["status"])
