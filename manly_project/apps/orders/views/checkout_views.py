from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from decimal import Decimal

from apps.accounts.models import UserAddress
from apps.cart.models import Cart


@login_required
def checkout_page(request):
    # 🔥 RESET checkout session every time
    request.session.pop("checkout_address_id", None)

    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        return redirect("cart_page")

    cart_items = []
    subtotal = Decimal("0.00")
    has_invalid_items = False

    for item in cart.items.select_related("product", "variant", "product__category"):
        product = item.product
        variant = item.variant

        is_invalid = (
            not product.is_active or
            not product.category.is_active or
            not variant.is_active or
            variant.stock < item.quantity
        )

        if is_invalid:
            has_invalid_items = True
        else:
            subtotal += product.base_price * item.quantity

        cart_items.append({
            "item": item,
            "product": product,
            "variant": variant,
            "line_total": product.base_price * item.quantity,
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
