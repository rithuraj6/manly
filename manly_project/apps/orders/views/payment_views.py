from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal

from apps.cart.models import Cart
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

    return render(request, "orders/payment.html", {
        "address": address,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
    })
