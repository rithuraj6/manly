
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from apps.accounts.decorators import user_required
from razorpay.errors import SignatureVerificationError
from apps.accounts.models import UserAddress
from decimal import Decimal
from apps.orders.models import Payment
from apps.wallet.models import AdminWalletTransaction
from apps.orders.utils.pricing import apply_offer

from apps.orders.services.order_creation import create_order
from apps.orders.utils.pricing import calculate_grand_total
from apps.wallet.services.wallet_services import pay_order_using_wallet
from apps.accounts.models import UserAddress
from django.contrib import messages
from django.urls import reverse
from apps.wallet.services.wallet_services import credit_admin_wallet
from django.db.models import Sum
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from apps.orders.services.get_order_preview import get_order_preview




        
@user_required
def payment_page(request):
    preview = get_order_preview(request)
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")
    

    address_snapshot = request.session.get("checkout_address_snapshot")
    if not address_snapshot:
        return redirect("checkout_page")
 

    wallet = getattr(request.user, "wallet", None)
    wallet_balance = wallet.balance if wallet else Decimal("0.00")
    
    
    breadcrumbs = [
        {"label": "Home", "url": reverse("home")},
        {"label": "Cart", "url": reverse("cart_page")},
        {"label": "Checkout", "url": reverse("checkout_page")},
        {"label": "Payment", "url": None},
    ]

    context = {
         "breadcrumbs": breadcrumbs, 
        "address": address_snapshot,
        "subtotal": preview["subtotal"],
        "coupon_discount": preview["coupon_discount"],
        "shipping": preview["delivery_fee"],
        "tax": preview["tax"],
        "total": preview["total_amount"],
        "wallet_balance": wallet_balance,
        "cod_allowed": preview["total_amount"] <= Decimal("5000"),
    }

    return render(request, "orders/payment.html", context)


@user_required
def create_razorpay_order(request):
    preview = get_order_preview(request)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(preview["total_amount"] * 100),
        "currency": "INR",
        "payment_capture": 1,
    })

    payment = Payment.objects.create(
        user=request.user,
        payment_method="razorpay",
        razorpay_order_id=razorpay_order["id"],
        amount=preview["total_amount"],
        status="initiated",
        address_snapshot=request.session["checkout_address_snapshot"],
    )

    return JsonResponse({
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": preview["total_amount"],
    })

@csrf_exempt
@transaction.atomic
def verify_razorpay_payment(request):
    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    payment = Payment.objects.select_for_update().get(
        razorpay_order_id=razorpay_order_id,
        status="initiated"
    )

    from apps.cart.models import Cart
    cart = Cart.objects.select_for_update().get(user=payment.user)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })
    except SignatureVerificationError:
        payment.status = "failed"
        payment.save(update_fields=["status"])
        return redirect("order_failure", payment_id=payment.id)

   
    payment.status = "success"
    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.save()

    coupon_id = request.session.get("applied_coupon_id")

    try:
        order = create_order(
            user=payment.user,
            cart=cart,
            address_snapshot=payment.address_snapshot,
            payment_method="razorpay",
            is_paid=True,
            coupon_id=coupon_id,
        )
    except ValueError as e:
        payment.status = "failed"
        payment.save(update_fields=["status"])
        messages.error(request, str(e))
        return redirect("payment_page")

    payment.order = order
    payment.save(update_fields=["order"])

    credit_admin_wallet(order=order, amount=order.total_amount)

    
    request.session.pop("applied_coupon_id", None)
    request.session.pop("coupon_discount", None)
    request.session.modified = True

    return redirect("order_success", order_id=order.order_id)



@user_required
def retry_payment(request,payment_id):
    payment = get_object_or_404(
        Payment,id=payment_id,user=request.user,status='failed'
    )
    
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET)
        
    )
    
    razorpay_order = client.order.create({
        'amount':int (payment.amount *100),
        'currency':'INR',
        'payment_capture':1
    })
    
    payment.razorpay_order_id = razorpay_order['id']
    payment.status='initiated'
    payment.save()
    
    return render(request,'orders/retry_payment.html',{
        'payment':payment,
        'razorpay_key': settings.RAZORPAY_KEY_ID
    })
    
    
    

    
@user_required
def order_failure(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        user=request.user,
        status="failed"
    )

    return render(request, "orders/order_failure.html", {
        "payment": payment
    })

   
    
@user_required
def wallet_payment(request):
    user = request.user
    cart = getattr(user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    address_snapshot = request.session.get("checkout_address_snapshot")
    if not address_snapshot:
        return redirect("checkout_page")

    coupon_id = request.session.get("applied_coupon_id")

    order = create_order(
        user=user,
        cart=cart,
        address_snapshot=address_snapshot,
        payment_method="wallet",
        is_paid=False,
        coupon_id=coupon_id,
    )

    try:
        pay_order_using_wallet(user=user, order=order)
    except ValueError as e:
        order.delete()
        messages.error(request, str(e))
        return redirect("payment_page")

    request.session.pop("applied_coupon_id", None)
    request.session.pop("coupon_discount", None)
    request.session.modified = True

    return redirect("order_success", order_id=order.order_id)

@user_required
def cod_payment(request):
    user = request.user
    cart = getattr(user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    address_snapshot = request.session.get("checkout_address_snapshot")
    if not address_snapshot:
        return redirect("checkout_page")

    coupon_id = request.session.get("applied_coupon_id")

    order = create_order(
        user=user,
        cart=cart,
        address_snapshot=address_snapshot,
        payment_method="cod",
        is_paid=False,
        coupon_id=coupon_id,
    )

   
    request.session.pop("applied_coupon_id", None)
    request.session.pop("coupon_discount", None)
    request.session.modified = True

    return redirect("order_success", order_id=order.order_id)
