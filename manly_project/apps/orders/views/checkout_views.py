from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from decimal import Decimal

from apps.accounts.models import UserAddress
from apps.cart.models import Cart


@login_required
def checkout_page(request):
    request.session.pop("checkout_address_id", None)
    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")

    for item in cart.items.select_related("variant", "product"):
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
        else:
            subtotal += product.base_price * cart_item.quantity

        cart_items.append({
            "item": cart_item,
            "product": product,
            "variant": variant,
            "line_total": product.base_price * cart_item.quantity,
            "is_invalid": is_invalid,
        })

    shipping = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal + shipping) * Decimal("0.18")).quantize(Decimal("0.01"))
    total = subtotal + shipping + tax

    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by("-is_default", "-id")

    context = {
        "cart_items": cart_items,
        "addresses": addresses,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total": total,
        "has_invalid_items": has_invalid_items,
    }

    return render(request, "orders/checkout.html", context)