from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Wishlist
from apps.products.models import Product

@login_required(login_url="login")
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, "wishlist/wishlist.html", {"wishlist": wishlist})


