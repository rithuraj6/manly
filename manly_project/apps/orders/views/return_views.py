from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import admin_required
from apps.accounts.decorators import user_required

from django.contrib import messages
from apps.orders.services.order_state import recalculate_order_status
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required

from apps.orders.utils.stock import restore_stock
from apps.orders.models import OrderItem, ReturnRequest


@user_required
def view_return_reason(request, item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status__in=["return_requested", "returned"]
    )

    return render(
        request,
        "orders/view_return_reason.html",
        {
            "order_item": order_item,
            "return_request": order_item.return_request,
        }
    )
    
@user_required
def request_return(request, item_id):
    item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user
    )

    if item.status != "delivered":
        messages.error(request, "This item is not eligible for return.")
        return redirect("order_detail", order_id=item.order.order_id)

   
    if hasattr(item, "return_request"):
        messages.warning(request, "Return already requested for this item.")
        return redirect("order_detail", order_id=item.order.order_id)

    if request.method == "POST":
        reason = request.POST.get("reason")
        description = request.POST.get("description", "")

        if not reason:
            messages.error(request, "Return reason is required.")
            return redirect(request.path)

        ReturnRequest.objects.create(
            user=request.user,
            order_item=item,
            reason=reason,
            description=description
        )

       
        item.status = "return_requested"
        item.save()

        messages.success(request, "Return request submitted successfully.")
        return redirect("order_detail", order_id=item.order.order_id)

    return render(request,"orders/request_return.html",{"item": item})




