from apps.orders.models import OrderItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from apps.orders.models import ReturnRequest ,OrderItem  
from apps.orders.services.order_state import recalculate_order_status



@login_required(login_url="admin_login")
def admin_return_request_list(request):
    returns = ReturnRequest.objects.select_related(
        "order_item",
        "order_item__order",
        "user"
    ).order_by("-created_at")

    return render(request,"adminpanel/returns/return_list.html",{"returns": returns})




@transaction.atomic
@login_required(login_url="admin_login")
def admin_approve_return(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    order_item = return_request.order_item

  
    if return_request.status != "pending":
        messages.error(request, "Return already processed")
        return redirect("admin_return_request_list")

    return_request.status = "approved"
    return_request.save(update_fields=['status'])

    order_item.status = OrderItem.STATUS_RETURNED
    order_item.save(update_fields=['status'])
    
    recalculate_order_status(order_item.order)
    
    
    messages.success(request, "Return approved successfully")
    return redirect("admin_return_request_list")



@login_required(login_url="admin_login")
def admin_reject_return(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)

    return_request.status = ReturnRequest.STATUS_REJECTED
    return_request.save()

    messages.error(request, "Return rejected")
    return redirect("admin_return_request_list")
