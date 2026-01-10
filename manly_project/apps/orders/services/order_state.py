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


def recalculate_order_state(order):
    items = order.items.all()

    active_items = items.exclude(
        status__in=["cancelled", "returned"]
    )

    if not active_items.exists():
        order.status = "fully_refunded"
    elif active_items.count() < items.count():
        order.status = "partially_refunded"
    else:
        order.status = "active"

    order.save(update_fields=["status"])
