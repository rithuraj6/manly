
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages
from apps.orders.services.order_state import recalculate_order_status
from apps.wallet.services.wallet_services import credit_admin_wallet
from django.db.models import Sum
from decimal import Decimal
from apps.orders.models import Order, OrderItem, OrderStatusHistory
from apps.orders.constants import ORDER_STATUS_FLOW


@login_required(login_url="admin_login")
def admin_order_list(request):
    orders = Order.objects.select_related("user").order_by("-created_at")

    search = request.GET.get("q", "").strip()
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(user__email__icontains=search) |
            Q(items__product__name__icontains=search)
        ).distinct()

    status = request.GET.get("status", "")
    if status:
        orders = orders.filter(status=status)

    payment = request.GET.get("payment", "")
    if payment:
        orders = orders.filter(payment_method=payment)

    sort = request.GET.get("sort", "")
    now = timezone.now()

    if sort == "newest":
        orders = orders.order_by("-created_at")
    elif sort == "oldest":
        orders = orders.order_by("created_at")
    elif sort == "amount_desc":
        orders = orders.order_by("-total_amount")
    elif sort == "amount_asc":
        orders = orders.order_by("total_amount")
    elif sort == "7d":
        orders = orders.filter(created_at__gte=now - timedelta(days=7))
    elif sort == "1m":
        orders = orders.filter(created_at__gte=now - timedelta(days=30))
    elif sort == "3m":
        orders = orders.filter(created_at__gte=now - timedelta(days=90))
    elif sort == "6m":
        orders = orders.filter(created_at__gte=now - timedelta(days=180))
    elif sort == "1y":
        orders = orders.filter(created_at__gte=now - timedelta(days=365))
    elif sort == "prev_year":
        orders = orders.filter(created_at__year=now.year - 1)

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "adminpanel/orders/order_list.html",
        {
            "orders": page_obj,
            "search": search,
            "status": status,
            "payment": payment,
            "sort": sort,
        }
    )


@login_required(login_url="admin_login")
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    items = OrderItem.objects.filter(order=order).select_related("product", "variant")

    allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

    return render(
        request,
        "adminpanel/orders/order_edit.html",
        {
            "order": order,
            "items": items,
            "allowed_next_statuses": allowed_next_statuses,
        }
    )


@login_required(login_url="admin_login")
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method != "POST":
        return redirect("admin_order_list")

    new_status = request.POST.get("status")
    allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

    if new_status not in allowed_next_statuses:
        messages.error(request, "Invalid status transition.")
        return redirect("admin_order_edit", order_id=order.order_id)

    
    if (
        new_status == "delivered"
        and order.payment_method == "cod"
        and not order.is_paid
    ):
        total_amount = (
            order.items.aggregate(
                total=Sum("final_price_paid")
            )["total"] or Decimal("0.00")
        )

        credit_admin_wallet(order=order, amount=total_amount)

        order.is_paid = True
        order.save(update_fields=["is_paid"])

    order.items.exclude(
        status__in=["cancelled", "returned"]
    ).update(status=new_status)

    recalculate_order_status(order)

    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by="admin",
    )

    messages.success(request, "Order status updated successfully")
    return redirect("admin_order_edit", order_id=order.order_id)












@login_required(login_url="admin_login")
def admin_order_update_success(request):
    return render(request, "adminpanel/orders/order_update_success.html")

