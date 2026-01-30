from django.http import JsonResponse
from apps.accounts.decorators import user_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.wishlist.models import Wishlist, WishlistItem
from apps.products.models import Product, ProductVariant
from apps.cart.views.ajax_views import add_to_cart
from apps.cart.models import CartItem

from django.views.decorators.http import require_GET




@user_required
@require_POST
def toggle_wishlist(request):
    product_uuid = request.POST.get("product_id")

    if not product_uuid:
        return JsonResponse({"success": False}, status=400)

    product = get_object_or_404(
        Product,
        uuid=product_uuid,
        is_active=True,
        category__is_active=True
    )

    wishlist,_= Wishlist.objects.get_or_create(user=request.user)

    # if not wishlist:
    #     wishlist = Wishlist.objects.create(user=request.user)

    item = WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).first()

    if item:
        item.delete()
        action = "removed"
    else:
        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product
        )
        action = "added"

    return JsonResponse({
        "success": True,
        "action": action,
        "wishlist_count": wishlist.items.count()
    })
    
    
    
    
@user_required
def wishlist_count(request):
    wishlist = getattr(request.user, "wishlist", None)
    count = wishlist.items.count() if wishlist else 0

    return JsonResponse({
        "wishlist_count": count
    })
    
    
@user_required
@require_POST
def remove_from_wishlist(request):
    product_uuid = request.POST.get("product_id")

    wishlist = getattr(request.user, "wishlist", None)
    if not wishlist:
        return JsonResponse({"success": False})

    WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).delete()

    return JsonResponse({
        "success": True,
        "wishlist_count": wishlist.items.count()
    })



@user_required
@require_POST
@transaction.atomic
def wishlist_add_to_cart(request):
    product_uuid = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")

    if not product_uuid or not variant_id or not variant_id.isdigit():
        return JsonResponse({
            "success": False,
            "message": "Please select a size before adding to cart"
        }, status=400)

    wishlist = getattr(request.user, "wishlist", None)
    if not wishlist:
        return JsonResponse({
            "success": False,
            "message": "Wishlist not found"
        }, status=400)

   
    if not WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).exists():
        return JsonResponse({
            "success": False,
            "message": "Item not in wishlist"
        }, status=400)

   
    add_to_cart(request)

    
    WishlistItem.objects.filter(
        wishlist=wishlist,
        product=product
    ).delete()

   
    cart_count = CartItem.objects.filter(
        cart__user=request.user
    ).count()

    wishlist_count = wishlist.items.count()

    return JsonResponse({
        "success": True,
        "cart_count": cart_count,
        "wishlist_count": wishlist_count,
    })


@user_required
@require_GET
def is_in_wishlist(request):
    product_uuid = request.GET.get("product_id")
    
    wishlist = getattr(request.user,"wishlist",None)
    
    exists = False
    
    if wishlist and product_id:
        exists = wishlist.items.filter(product=product).exists()
        
    return JsonResponse({
        "in_wishlist":exists
    })