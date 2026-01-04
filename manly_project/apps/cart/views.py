from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cart
from apps.products.models import Product


@login_required(login_url="login")
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, "cart/cart.html", {"cart": cart})


