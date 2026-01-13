import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from razorpay.errors import SignatureVerificationError
from apps.accounts.models import UserAddress
from decimal import Decimal
from apps.orders.models import Payment
from apps.orders.services.order_creation import create_order
from apps.orders.utils.pricing import calculate_grand_total

from apps.accounts.models import UserAddress


@login_required
def payment_page(request):
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")

    
    if request.method == "POST":
        address_id = request.POST.get("address_id")
        if not address_id:
            messages.error(request, "Please select an address")
            return redirect("checkout_page")

        request.session["checkout_address_id"] = address_id

    address_id = request.session.get("checkout_address_id")
    if not address_id:
        return redirect("checkout_page")

    address = UserAddress.objects.get(id=address_id, user=request.user)

    subtotal = Decimal("0.00")
    for item in cart.items.select_related("product"):
        subtotal += item.product.base_price * item.quantity

    shipping = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + shipping) * Decimal("0.18")).quantize(Decimal("0.01"))
    total = subtotal + shipping + tax

    return render(request, "orders/payment.html", { "address": address,"subtotal": subtotal,"shipping": shipping,"tax": tax,"total": total,})



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

    

@login_required
def verify_razorpay_payment(request):
    data = request.POST

    payment = get_object_or_404(
        Payment,
        razorpay_order_id=data.get("razorpay_order_id"),
        status="initiated"
    )

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data.get("razorpay_order_id"),
            "razorpay_payment_id": data.get("razorpay_payment_id"),
            "razorpay_signature": data.get("razorpay_signature"),
        })
    except SignatureVerificationError:
        payment.status = "failed"
        payment.save()
        return redirect("order_failure", payment_id=payment.id)

    payment.razorpay_payment_id = data.get("razorpay_payment_id")
    payment.razorpay_signature = data.get("razorpay_signature")
    payment.status = "success"
    payment.save()

    order = create_order(
        user=payment.user,
        cart=payment.user.cart,
        address_snapshot=payment.address_snapshot,
        payment_method="razorpay",
        is_paid=True
    )
    payment.order = order
    payment.save()

    return redirect("order_success", order_id=order.order_id)


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