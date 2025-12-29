from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Wishlist
from apps.products.models import Product

@login_required(login_url="login")
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "wishlist/wishlist.html", {"wishlist": wishlist})


@login_required(login_url="login")
def add_to_wishlist(request, product_id):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.add(product)
    return redirect("wishlist")


@login_required(login_url="login")
def remove_from_wishlist(request, product_id):
    wishlist = Wishlist.objects.get(user=request.user)
    product = get_object_or_404(Product, id=product_id)
    wishlist.products.remove(product)
    return redirect("wishlist")
