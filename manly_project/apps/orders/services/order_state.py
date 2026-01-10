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

   
    if items.filter(status="pending").exists():
        order.status = "pending"

  
    elif items.filter(status="shipped").exists():
        order.status = "shipped"

  
    
    elif items.filter(status="out_for_delivery").exists():
        order.status = "out_for_delivery"

    
    elif (
        items.filter(status="cancelled").exists()
        and items.exclude(status="cancelled").exists()
    ):
        order.status = "partially_refunded"

   
    elif items.filter(status="cancelled").count() == items.count():
        order.status = "cancelled"

    
    elif items.filter(status="delivered").count() == items.count():
        order.status = "delivered"

    order.save(update_fields=["status"])
