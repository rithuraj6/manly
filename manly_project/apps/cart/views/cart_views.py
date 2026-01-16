from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.cart.models import Cart
from apps.orders.utils.pricing import apply_offer, get_best_offer



@login_required(login_url="login")
def cart_page(request):
    cart_items = []
    subtotal = 0
    has_invalid_items = False

    cart = getattr(request.user, "cart", None)

    if cart:
        for item in cart.items.select_related("product", "variant", "product__category"):
            product = item.product
            variant = item.variant

            is_invalid = (
                not product.is_active or
                not product.category.is_active or
                not variant.is_active or
                variant.stock <= 0
            )

            if is_invalid:
                has_invalid_items = True
                discounted_price = product.base_price
                line_total = Decimal("0.00")
            else:
                discounted_price = apply_offer(product, product.base_price)
                line_total = discounted_price * item.quantity
                subtotal += line_total

            cart_items.append({
                "item": item,
                "product": product,
                "variant": variant,
                "image": product.images.first(),
                "base_price": product.base_price,
                "discounted_price": discounted_price,
                "line_total": line_total,
                "is_invalid": is_invalid,
            })

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Cart", "url": None},
    ]

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "breadcrumbs": breadcrumbs,
        "has_invalid_items": has_invalid_items,
    }

    return render(request, "cart/cart.html", context)