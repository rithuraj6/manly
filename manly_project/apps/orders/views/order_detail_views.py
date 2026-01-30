from django.shortcuts import render, get_object_or_404
from apps.accounts.decorators import user_required
from decimal import Decimal

from apps.orders.models import Order


@user_required
def order_detail(request, order_uuid):

    order = get_object_or_404(
        Order,
        uuid=order_uuid,
        user=request.user
    )

    items = (
        order.items
        .select_related("product", "variant")
        .prefetch_related("product__images", "return_request")
    )

    
    paid_total = order.total_amount

    refunded_total = sum(
        item.final_price_paid
    for item in items
        if item.status in ["cancelled", "returned"]
    )

    net_paid = paid_total - refunded_total
    payable_total = paid_total-refunded_total
     
    invoice_items = items.filter(
        status__in=["delivered", "returned"]
    )

    can_download_invoice = invoice_items.exists()

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "My Account", "url": "/accounts/profile/"},
        {"label": "My Orders", "url": "/orders/"},
    ]

    context = {
        "order": order,
        "items": items,

        
        "paid_total": paid_total,
        "refunded_total": refunded_total,
        "payable_total": payable_total,

        "can_download_invoice": can_download_invoice,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "orders/order_detail.html", context)
