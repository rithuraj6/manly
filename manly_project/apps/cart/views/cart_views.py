from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.cart.models import Cart

@login_required(login_url="login")
def cart_page(request):
    cart_items = []
    subtotal = 0
    has_invalid_items = False

    cart = getattr(request.user, "cart", None)

    if cart:
        for item in cart.items.select_related(
            "product", "variant", "product__category"
        ).prefetch_related("product__images"):

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
            else:
                subtotal += product.base_price * item.quantity

            cart_items.append({
                "item": item,
                "product": product,
                "variant": variant,
                "image": product.images.first(),  
                "is_invalid": is_invalid,
                "line_total": (
                    product.base_price * item.quantity if not is_invalid else 0
                )
            })
            
    breadcrumbs = [
    {"name": "Home", "url": "/"},
    {"name": "Cart", "url": None},
]          
    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "has_invalid_items": has_invalid_items,
}
       
  
    return render(request, "cart/cart.html", context)
