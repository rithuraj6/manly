
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
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


@login_required
def payment_page(request):
    cart = getattr(request.user,'cart',None)
    if not cart or not cart.items.exists():
        return redirect('cart_page')
    
    
    if request.method == 'POST'and 'address_id' in request.POST:
        address_id = request.POST.get('address_id')
        
        if not address_id:
            messages.error(request,'Please select an address')
            return redirect ('checkout_page')
        
        
        request.session['checkout_address_id']=address_id
        return redirect('payment_page')
    
    
    
    address_id = request.session.get('checkout_address_id')
    if not address_id:
        return redirect('checkout_page')
    
    address = UserAddress.objects.get(id=address_id,user=request.user)
    
    subtotal = Decimal("0.00")
    for item in cart.items.select_related("product", "variant", "product__category"):
        discounted_price = apply_offer(item.product, item.product.base_price)
        subtotal += discounted_price * item.quantity
        
        
    shipping = Decimal('0.00')if subtotal>=3000 else Decimal('150.00')
    tax = ((subtotal+shipping)*Decimal('0.18')).quantize(Decimal('0.01'))
    total = subtotal + shipping + tax
    wallet = getattr(request.user, "wallet", None)
    wallet_balance = wallet.balance if wallet else Decimal("0.00")

    cod_allowed = total <= Decimal("5000.00")
    breadcrumbs = [
    {"label": "Home", "url": "/"},
    {"label": "Cart",  "url": reverse("cart_page")},
    {"label": "Checkoutpage", "url":"checkout/"},
    {"label": "Paymentpage", "url":None},
    ]
    
    context={
        "breadcrumbs":breadcrumbs,
        "address": address,
            "subtotal": subtotal,
            "shipping": shipping,
            "tax": tax,
            "total": total,

            "wallet_balance": wallet_balance,
            "cod_allowed": cod_allowed,
    } 

    return render(  request,"orders/payment.html",context)
        
    
@login_required
def create_razorpay_order(request):
    user = request.user
    amount = calculate_grand_total(user)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    address_id = request.session.get("checkout_address_id")
    address = UserAddress.objects.get(id=address_id, user=user)

    payment = Payment.objects.create(
        user=user,
        payment_method="razorpay",
        razorpay_order_id=razorpay_order["id"],
        amount=amount,
        status="initiated",
        address_snapshot={
            "full_name": address.full_name,
            "phone": address.phone,
            "house_name": address.house_name,
            "street": address.street,
            "land_mark": address.land_mark,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "pincode": address.pincode,
        }
    )

    return JsonResponse({
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount
    })

    

@csrf_exempt
@transaction.atomic
def verify_razorpay_payment(request):
    if request.method != "POST":
        return redirect("cart_page")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    payment = Payment.objects.select_for_update().get(
        razorpay_order_id=razorpay_order_id,
        status="initiated"
    )

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
    payment.save(update_fields=[
        "status",
        "razorpay_payment_id",
        "razorpay_signature"
    ])

    
    if payment.order:
        order = payment.order
    else:
        order = create_order(
            user=payment.user,
            cart=payment.user.cart,
            address_snapshot=payment.address_snapshot,
            payment_method="razorpay",
            is_paid=True,
        )
    payment.order = order
    payment.save(update_fields=["order"])

   
    total_amount = (
        order.items.aggregate(
            total=Sum("final_price_paid")
        )["total"] or Decimal("0.00")
    )

    credit_admin_wallet(order=order, amount=total_amount)

    return redirect("order_success", order_id=order.order_id)




@login_required
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
    
    
    

    

@login_required
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

   
    
@login_required
def wallet_payment(request):
    user = request.user
    cart = getattr(user, "cart", None)

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    address_id = request.session.get("checkout_address_id")
    if not address_id:
        return redirect("checkout_page")

    address = UserAddress.objects.get(id=address_id, user=user)

    order = create_order(
        user=user,
        cart=cart,
        address_snapshot={
            "full_name": address.full_name,
            "phone": address.phone,
            "house_name": address.house_name,
            "street": address.street,
            "land_mark": address.land_mark,
            "city": address.city,
            "state": address.state,
            "country": address.country,
            "pincode": address.pincode,
        },
        payment_method="wallet",
        is_paid=False 
    )

    try:
        pay_order_using_wallet(user=user, order=order)
    except ValueError as e:
        order.delete()  
        messages.error(request, str(e))
        return redirect("payment_page")

    return redirect("order_success", order_id=order.order_id)