from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.orders.models import Order, OrderItem



@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        order_id=order_id,
        user=request.user
    )

    items = (
        order.items
        .select_related("product", "variant")
        .prefetch_related("product__images","return_request")
        
    )
    
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
    "invoice_items": invoice_items,
    "can_download_invoice": can_download_invoice,
    "breadcrumbs": breadcrumbs,
    }


    return render(request, "orders/order_detail.html", context)