from django.db.models import Sum
from django.db.models.functions import TruncDay, TruncMonth
from apps.orders.models import OrderItem
from apps.orders.models import Order
from django.db.models.functions import TruncDate
from django.db.models import Count



VALID_ORDER_STATUSES = [
    "confirmed",
    "shipped",
    "delivered"
]

def get_revenue_timeseries(start_date, end_date):
    qs = (
        Order.objects
        .filter(
            created_at__date__range=(start_date, end_date),
            status__in=VALID_ORDER_STATUSES
        )
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    labels = [row["day"].strftime("%Y-%m-%d") for row in qs]
    data = [row["count"] for row in qs]

    return {
        "labels": labels,
        "data": data
    }