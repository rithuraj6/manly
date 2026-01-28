from apps.orders.models import OrderItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from apps.orders.models import ReturnRequest ,OrderItem  
from apps.orders.services.order_state import recalculate_order_status
from apps.orders.utils.stock import restore_stock
from decimal import Decimal
from apps.wallet.models import Wallet,WalletTransaction
from apps.orders.models import Payment
from apps.wallet.services.wallet_services import refund_to_wallet
from django.core.paginator import Paginator
from apps.orders.models import ReturnRequest


@login_required(login_url="admin_login")
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
def approve_return(request, return_id):
    return_request = get_object_or_404(
        ReturnRequest,
        id=return_id,
        status=ReturnRequest.STATUS_PENDING
    )

    order_item = return_request.order_item
    order = order_item.order

    return_request.status = ReturnRequest.STATUS_APPROVED
    return_request.save(update_fields=["status"])

    order_item.status = OrderItem.STATUS_RETURNED
    order_item.save(update_fields=["status"])

    restore_stock(order_item)


    refund_to_wallet(
        user=order.user,
        order_item=order_item,
        amount=order_item.final_price_paid,
        reason=f"Refund for returned item ({order.order_id})",
    )

    recalculate_order_status(order)

    messages.success(request, "Return approved and refund credited to user wallet.")
    return redirect("admin_return_request_list")




@login_required(login_url="admin_login")
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
