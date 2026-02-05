from apps.orders.models import OrderItem
from django.shortcuts import render, get_object_or_404, redirect
from apps.accounts.decorators import admin_required
from django.contrib import messages
from django.db import transaction
from apps.orders.models import ReturnRequest ,OrderItem  
from apps.orders.services.order_state import recalculate_order_status
from apps.orders.utils.stock import restore_stock
from apps.orders.services.refund_service import process_refund
from apps.orders.constants import RefundEvent

from django.core.paginator import Paginator
from apps.orders.models import ReturnRequest


@admin_required
def admin_return_request_list(request):
    
    
    
    
    returns_qs= ReturnRequest.objects.select_related(
        "order_item",
        "order_item__order",
        "user"
    ).order_by("-created_at")
    paginator = Paginator(returns_qs, 11)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request,"adminpanel/returns/return_list.html",{"returns": page_obj,"page_obj":page_obj})




@transaction.atomic
@admin_required
def approve_return(request, return_id):
    return_request = get_object_or_404(
        ReturnRequest,
        id=return_id,
        status=ReturnRequest.STATUS_PENDING
    )

    order_item = return_request.order_item
    order = order_item.order
    
    process_refund(order_item=order_item,
                   event=RefundEvent.RETURN_APPROVED,
                   initiated_by="admin",
                   )
    
    restore_stock(order_item)

    
  
    order_item.status = OrderItem.STATUS_RETURNED
    order_item.save(update_fields=["status"])
    return_request.status = ReturnRequest.STATUS_APPROVED
    return_request.save(update_fields=["status"])
    
    


    recalculate_order_status(order)

    messages.success(request, "Return approved and refund credited to user wallet.")
    return redirect("admin_return_request_list")



@admin_required
def admin_reject_return(request, return_id):
    return_request = get_object_or_404(
        ReturnRequest,
        id=return_id,
        status=ReturnRequest.STATUS_PENDING
    )

    return_request.status = ReturnRequest.STATUS_REJECTED
    return_request.save(update_fields=["status"])

    messages.error(request, "Return rejected")
    return redirect("admin_return_request_list")
