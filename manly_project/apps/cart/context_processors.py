def cart_count(request):
    if request.user.is_authenticated:
        cart = getattr(request.user, "cart", None)
        if cart:
            return {
                "cart_count": sum(item.quantity for item in cart.items.all())
            }
    return {"cart_count": 0}
