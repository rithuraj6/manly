from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from decimal import Decimal
from django.contrib import messages
from apps.accounts.models import UserAddress
from apps.cart.models import Cart
from apps.orders.utils.pricing import apply_offer
from django.urls import reverse




@login_required
def checkout_page(request):
    request.session.pop("checkout_address_id", None)
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")

    for item in cart.items.select_related("variant", "product"):
        if item.quantity > 10:
            messages.error(
                request,
                f"{item.product.name} exceeds max allowed quantity (10). Please update cart."
            )
            return redirect("cart_page")

        if item.quantity > item.variant.stock:
            messages.error(
                request,
                f"{item.product.name} ({item.variant.size}) stock reduced. Please update cart."
            )
            return redirect("cart_page")

    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")

    cart_items = []
    subtotal = Decimal("0.00")
    has_invalid_items = False

    for cart_item in cart.items.select_related("product", "variant", "product__category"):
        product = cart_item.product
        variant = cart_item.variant

        is_invalid = (
            not product.is_active or
            not product.category.is_active or
            not variant.is_active or
            variant.stock <= 0
        )

        if cart_item.quantity > variant.stock:
            messages.error(
                request,
                f"{product.name} only has {variant.stock} left. Cart updated."
            )
            cart_item.quantity = variant.stock
            cart_item.save()
            return redirect("cart_page")

        if is_invalid:
            has_invalid_items = True
            discounted_price = product.base_price
            line_total = Decimal("0.00")
        else:
            discounted_price = apply_offer(product, product.base_price)
            line_total = discounted_price * cart_item.quantity
            subtotal += line_total

        cart_items.append({
            "item": cart_item,
            "product": product,
            "variant": variant,
            "base_price": product.base_price,
            "discounted_price": discounted_price,
            "line_total": line_total,
            "is_invalid": is_invalid,
        })
        
    
    delivery_fee = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + delivery_fee) * Decimal("0.18")).quantize(Decimal("0.01"))
    total_amount = subtotal + delivery_fee + tax
    
    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by("-is_default", "-id")
    
    
    
    breadcrumbs = [
    {"label": "Home", "url": "/"},
    {"label": "Cart", "url": reverse("cart_page")},
    {"label": "Checkoutpage", "url":None},
    ] 

    context = {
        "cart_items": cart_items,
        "addresses": addresses,
        "subtotal": subtotal,
        "delivery_fee":delivery_fee,
       "delivery_fee": delivery_fee,
       "breadcrumbs":breadcrumbs,
        "tax": tax,
        "total_amount": total_amount,
        "has_invalid_items": has_invalid_items,
    }

    return render(request, "orders/checkout.html", context)