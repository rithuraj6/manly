from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart, CartItem
from apps.products.models import Product


@login_required(login_url="login")
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart/cart.html", {"cart": cart})


@login_required(login_url="login")
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
        item.save()

    return redirect("cart")


@login_required(login_url="login")
def remove_from_cart(request, item_id):
    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__user=request.user
    )
    item.delete()
    return redirect("cart")
