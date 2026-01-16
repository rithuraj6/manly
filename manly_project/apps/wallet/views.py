import razorpay
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from apps.wallet.models import WalletTransaction, Wallet
from apps.orders.models import Payment

from django.urls import reverse
client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


@login_required
def wallet_page(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    transactions_qs = (
        WalletTransaction.objects
        .filter(wallet=wallet)
        .select_related("order")
        .order_by("-created_at")
    )
    paginator = Paginator(transactions_qs, 8)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    
    breadcrumbs = [
    {"label": "Home", "url": "/"},
     {"label": "Account", "url": reverse("account_profile")},
     {"label": "Wallet",  "url": None},
    
    
    ]
    
    context={
        "breadcrumbs":breadcrumbs,
        "wallet": wallet,
             "transactions": page_obj,
             "page_obj": page_obj,
        
    }
    return render(   request,"wallet/wallet.html",context)


@require_POST
@login_required
def create_wallet_topup_order(request):
    amount = Decimal(request.POST.get("amount", "0"))

    if amount < 10:
        return JsonResponse({
            "success": False,
            "message": "Minimum top-up amount is ₹10"
        })

    razorpay_order = client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    payment = Payment.objects.create(
        user=request.user,
        amount=amount,
        payment_method="razorpay",
        razorpay_order_id=razorpay_order["id"],
        status="pending"
    )

    return JsonResponse({
        "success": True,
        "order_id": razorpay_order["id"],
        "amount": int(amount * 100),
        "key": settings.RAZORPAY_KEY_ID,
        "payment_id": payment.id
    })


@require_POST
@login_required
def verify_wallet_payment(request):
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")
    payment_id = request.POST.get("payment_id")

    payment = Payment.objects.get(id=payment_id, user=request.user)

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        payment.status = "failed"
        payment.save()
        return JsonResponse({"success": False})

    payment.status = "success"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.save()

    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.balance += payment.amount
    wallet.save()

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=payment.amount,
        txn_type=WalletTransaction.CREDIT,
        reason="Wallet Top-up",
        payment=payment
    )

    return JsonResponse({"success": True})
