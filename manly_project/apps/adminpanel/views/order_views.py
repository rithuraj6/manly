# from django.shortcuts import render ,get_object_or_404,redirect
# from django.contrib.auth.decorators import user_passes_test
# from django.core.paginator import Paginator
# from django.db.models import Q
# from django.contrib.auth.decorators import login_required

# from apps.orders.models import Order,OrderItem,OrderStatusHistory
# from apps.orders.constants import ORDER_STATUS_FLOW
# from django.contrib import messages



# @login_required(login_url="admin_login")
# def admin_order_list(request):

#     orders = Order.objects.select_related("user").order_by("-created_at")

#     # --------------------
#     # SEARCH
#     # --------------------
#     search = request.GET.get("q", "").strip()
#     if search:
#         orders = orders.filter(
#             Q(order_id__icontains=search) |
#             Q(user__email__icontains=search) |
#             Q(items__product__name__icontains=search)
#         ).distinct()

#     # --------------------
#     # FILTERS
#     # --------------------
#     status = request.GET.get("status", "")
#     if status:
#         orders = orders.filter(status=status)

#     payment = request.GET.get("payment", "")
#     if payment:
#         orders = orders.filter(payment_method=payment)

#     # --------------------
#     # SORTING
#     # --------------------
#     sort = request.GET.get("sort", "")
#     now = timezone.now()

#     if sort == "newest":
#         orders = orders.order_by("-created_at")

#     elif sort == "oldest":
#         orders = orders.order_by("created_at")

#     elif sort == "amount_desc":
#         orders = orders.order_by("-total_amount")

#     elif sort == "amount_asc":
#         orders = orders.order_by("total_amount")

#     # --------------------
#     # DATE-BASED FILTERS (NEW)
#     # --------------------
#     elif sort == "7d":
#         orders = orders.filter(created_at__gte=now - timedelta(days=7))

#     elif sort == "1m":
#         orders = orders.filter(created_at__gte=now - timedelta(days=30))

#     elif sort == "3m":
#         orders = orders.filter(created_at__gte=now - timedelta(days=90))

#     elif sort == "6m":
#         orders = orders.filter(created_at__gte=now - timedelta(days=180))

#     elif sort == "1y":
#         orders = orders.filter(created_at__gte=now - timedelta(days=365))

#     elif sort == "prev_year":
#         orders = orders.filter(created_at__year=now.year - 1)

#     # --------------------
#     # PAGINATION
#     # --------------------
#     paginator = Paginator(orders, 6)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(
#         request,
#         "adminpanel/orders/order_list.html",
#         {
#             "orders": page_obj,
#             "search": search,
#             "status": status,
#             "payment": payment,
#             "sort": sort,
#         }
#     )


# @login_required(login_url='admin_login')
# def admin_order_edit(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id)

#     print("DEBUG ORDER STATUS =", order.status)
#     print("DEBUG FLOW =", ORDER_STATUS_FLOW)
#     print("DEBUG ALLOWED =", ORDER_STATUS_FLOW.get(order.status))

#     items = (
#         OrderItem.objects
#         .filter(order=order)
#         .select_related("product", "variant")
#     )

#     allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

#     return render(
#         request,
#         "adminpanel/orders/order_edit.html",
#         {
#             "order": order,
#             "items": items,
#             "allowed_next_statuses": allowed_next_statuses,
#         }
#     )

# @login_required(login_url='admin_login')
# def admin_order_update(request, order_id):
#     order = get_object_or_404(Order, order_id=order_id)

#     if request.method != "POST":
#         return redirect("admin_order_list")

#     if order.status in ["delivered", "cancelled", "refunded"]:
#         messages.error(request, "This order can no longer be modified")
#         return redirect("admin_order_edit", order_id=order.order_id)

#     new_status = request.POST.get("status")
#     allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

#     if new_status not in allowed_next_statuses:
#         messages.error(
#             request,
#             f"Invalid status transition from {order.status} to {new_status}"
#         )
#         return redirect("admin_order_edit", order_id=order.order_id)

#     order.status = new_status
#     order.save()

#     order.items.update(status=new_status)

#     OrderStatusHistory.objects.create(
#         order=order,
#         status=new_status,
#         changed_by="admin"
#     )

#     messages.success(request, "Order status updated successfully")
#     return redirect("admin_order_edit", order_id=order.order_id)



# @login_required(login_url="admin_login")
# def admin_order_update_success(request):
#     return render(request,"adminpanel/orders/order_update_success.html")
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.contrib import messages

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

    paginator = Paginator(orders, 6)
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

    if order.status in ["delivered", "cancelled"]:
        messages.error(request, "This order can no longer be modified")
        return redirect("admin_order_edit", order_id=order.order_id)

    new_status = request.POST.get("status")
    allowed_next_statuses = ORDER_STATUS_FLOW.get(order.status, [])

    if new_status not in allowed_next_statuses:
        messages.error(request, "Invalid status transition")
        return redirect("admin_order_edit", order_id=order.order_id)

    order.status = new_status
    order.save()

    order.items.exclude(
    status__in=["cancelled", "returned"]
    ).update(status=new_status)
    OrderStatusHistory.objects.create(
        order=order,
        status=new_status,
        changed_by="admin"
    )

    messages.success(request, "Order status updated")
    return redirect("admin_order_edit", order_id=order.order_id)

@login_required(login_url="admin_login")
def admin_order_update_success(request):
    return render(
        request,
        "adminpanel/orders/order_update_success.html"
    )