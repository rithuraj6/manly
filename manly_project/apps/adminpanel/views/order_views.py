from django.shortcuts import render ,get_object_or_404,redirect
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from apps.orders.models import Order,OrderItem,OrderStatusHistory
from apps.orders.constants import ORDER_STATUS_FLOW
from django.contrib import messages



@login_required(login_url='admin_login')
def admin_order_list(request):

    orders = Order.objects.select_related("user").order_by("-created_at")


    search = request.GET.get("q", "").strip()
    if search:
        orders = orders.filter(
            Q(order_id__icontains=search) |
            Q(user__email__icontains=search)
        )


    status_filters = request.GET.getlist("status")
    if status_filters:
        orders = orders.filter(status__in=status_filters)

    payment_filters = request.GET.getlist("payment")
    if payment_filters:
        orders = orders.filter(payment_method__in=payment_filters)


    sort = request.GET.get("sort")

    if sort == "newest":
        orders = orders.order_by("-created_at")

    elif sort == "oldest":
        orders = orders.order_by("created_at")

    elif sort in ["pending", "shipped", "out_for_delivery", "delivered", "returned", "refunded"]:
        orders = orders.filter(status=sort)

    elif sort == "month_asc":
        orders = orders.order_by("created_at")

    elif sort == "month_desc":
        orders = orders.order_by("-created_at")

   
    paginator = Paginator(orders, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "adminpanel/orders/order_list.html",
        {
            "orders": page_obj,
            "search": search,
            "status_filters": status_filters,
            "payment_filters": payment_filters,
            "sort": sort,
        }
    )


@login_required(login_url='admin_login')
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    items = (
        OrderItem.objects
        .filter(order=order)
        .select_related("product", "variant")
    )

    # Allowed next statuses based on current status
    allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

    context = {
        "order": order,
        "items": items,
        "allowed_next_statuses": allowed_next_statuses,
    }

    return render(
        request,
        "adminpanel/orders/order_edit.html",
        context
    )

@login_required(login_url='admin_login')
def admin_order_update(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if request.method != "POST":
        return redirect("admin_order_list")

    new_status = request.POST.get("status")

    allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

    if new_status not in allowed_next_statuses:
        messages.error(
            request,
            f"Invalid status transition from {order.status} to {new_status}"
        )
        return redirect("admin_order_edit", order_id=order.order_id)

    # 🔒 Final locks
    if order.status in ["delivered", "cancelled", "refunded"]:
        messages.error(request, "This order can no longer be modified")
        return redirect("admin_order_edit", order_id=order.order_id)

    # ✅ Update order
    order.status = new_status
    order.save()

    # ✅ Sync items
    order.items.update(status=new_status)

    # ✅ History
    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by="admin"
    )

    messages.success(request, "Order status updated successfully")
    return redirect("admin_order_edit", order_id=order.order_id)

@login_required(login_url="admin_login")
def admin_order_update_success(request):
    return render(
        request,
        "adminpanel/orders/order_update_success.html"
    )
