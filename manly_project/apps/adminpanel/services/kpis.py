from datetime import timedelta
from django.db.models import Sum
from apps.orders.models import Order, OrderItem

VALID_ORDER_STATUSES = [
    "delivered",
    "shipped",
    "confirmed"
]


def _get_period_kpis(start_date, end_date):
    
    orders_qs = Order.objects.filter(
        created_at__date__range=(start_date, end_date),
        status__in=VALID_ORDER_STATUSES
    )

    items_qs = OrderItem.objects.filter(
        order__created_at__date__range=(start_date, end_date),
        order__status__in=VALID_ORDER_STATUSES
    )

    revenue = items_qs.aggregate(
        total=Sum("final_price_paid")
    )["total"] or 0

    products_sold = items_qs.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    return {
        "revenue": revenue,
        "orders": orders_qs.count(),
        "products_sold": products_sold,
        "customers": orders_qs.values("user").distinct().count(),
    }


def _growth(current, previous):
    
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)


def get_kpis_with_growth(start_date, end_date):
   
    duration = (end_date - start_date).days
    prev_start = start_date - timedelta(days=duration + 1)
    prev_end = start_date - timedelta(days=1)

    current = _get_period_kpis(start_date, end_date)
    previous = _get_period_kpis(prev_start, prev_end)

    return {
        "revenue": {
            "value": current["revenue"],
            "growth": _growth(current["revenue"], previous["revenue"]),
        },
        "orders": {
            "value": current["orders"],
            "growth": _growth(current["orders"], previous["orders"]),
        },
        "products_sold": {
            "value": current["products_sold"],
            "growth": _growth(current["products_sold"], previous["products_sold"]),
        },
        "customers": {
            "value": current["customers"],
            "growth": _growth(current["customers"], previous["customers"]),
        },
    }
