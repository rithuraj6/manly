from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import admin_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from apps.orders.models import Order, OrderItem


@admin_required
def admin_order_list(request):
    orders = (
        Order.objects
        .select_related("user")
        .order_by("-created_at")
    )

    search = request.GET.get("q", "").strip()
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(user__email__icontains=search)
        )

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "adminpanel/orders/order_list.html",
        {"orders": page_obj, "search": search}
    )


@admin_required
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    items = order.items.select_related("product", "variant")

    return render(
        request,
        "adminpanel/orders/order_edit.html",
        {"order": order, "items": items}
    )


@admin_required
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        order.status = new_status
        order.save()

        order.items.update(status=new_status)

        messages.success(request, "Order status updated")

    return redirect("admin_order_edit", order_id=order.order_id)

@admin_required
def admin_order_update_success(request):
    return render(request, "adminpanel/orders/order_update_success.html")
