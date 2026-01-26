import csv
from django.http import HttpResponse
from apps.orders.models import OrderItem

VALID_ORDER_STATUSES = [
    "confirmed",
    "shipped",
    "delivered"
]


def export_sales_csv(start_date, end_date):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=sales_report.csv"

    writer = csv.writer(response)
    writer.writerow([
        "Order ID",
        "Order Date",
        "Customer",
        "Product",
        "Quantity",
        "Final Price Paid",
        "Payment Method",
        "Order Status"
    ])

    items = (
        OrderItem.objects
        .select_related("order", "product")
        .filter(
            order__created_at__date__range=(start_date, end_date),
            order__status__in=VALID_ORDER_STATUSES
        )
    )

    for item in items:
        writer.writerow([
            item.order.order_id,
            item.order.created_at.date(),
            item.order.user.email,
            item.product.name,
            item.quantity,
            item.final_price_paid,
            item.order.payment_method,
            item.order.status,
        ])

    return response
