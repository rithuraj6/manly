from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404 ,render

from apps.cart.models import Cart, CartItem
from apps.products.models import Product, ProductVariant


MAX_QTY_PER_ITEM = 10



@require_POST
@login_required(login_url="login")
def add_to_cart(request):
    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    qty = int(request.POST.get("quantity", 1))

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
        category__is_active=True
    )

    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        product=product,
        is_active=True
    )

    if variant.stock <= 0:
        return JsonResponse({
            "success": False,
            "message": "Product is currently out of stock"
        }, status=400)

    cart, _ = Cart.objects.get_or_create(
        user=request.user,
        defaults={"is_active": True}
    )

   

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={"quantity": 0}
    )

    new_quantity = cart_item.quantity + qty

    if new_quantity > MAX_QTY_PER_ITEM:
        return JsonResponse({
            "success": False,
            "message": "Maximum 10 units allowed per product"
        }, status=400)

    if new_quantity > variant.stock:
        return JsonResponse({
            "success": False,
            "message": "Requested quantity exceeds available stock"
        }, status=400)

    cart_item.quantity = new_quantity
    cart_item.save()

    cart_count = sum(item.quantity for item in cart.items.all())

    return JsonResponse({
        "success": True,
        "message": "Item added to cart",
        "cart_count": cart_count,
        "item_quantity": cart_item.quantity
    })
    

@require_POST
@login_required(login_url="login")
def update_cart_qty(request):
    item_id = request.POST.get("item_id")
    action = request.POST.get("action")

    cart = getattr(request.user, "cart", None)
    if not cart:
        return JsonResponse({"success": False})

    item = CartItem.objects.select_related("variant", "product").filter(
        id=item_id, cart=cart
    ).first()

    if not item:
        return JsonResponse({"success": False})

    if action == "plus":
        if item.quantity >= item.variant.stock:
            return JsonResponse({
                "success": False,
                "message": f"Only {item.variant.stock} left in stock"
            })
        item.quantity += 1

    elif action == "minus":
        if item.quantity <= 1:
            return JsonResponse({"success": False})
        item.quantity -= 1

    item.save()

    cart_count = sum(i.quantity for i in cart.items.all())

    return JsonResponse({
        "success": True,
        "quantity": item.quantity,
        "line_total": item.quantity * item.product.base_price,
        "cart_count": cart_count
    })
    

@require_POST
@login_required(login_url="login")
def change_cart_variant(request):
    item_id = request.POST.get("item_id")
    new_variant_id = request.POST.get("variant_id")

    cart = getattr(request.user, "cart", None)
    if not cart:
        return JsonResponse({"success": False})

    item = CartItem.objects.filter(id=item_id, cart=cart).first()
    if not item:
        return JsonResponse({"success": False})

    new_variant = ProductVariant.objects.filter(
        id=new_variant_id,
        product=item.product,
        is_active=True
    ).first()

    if not new_variant:
        return JsonResponse({"success": False})

   
    existing_item = CartItem.objects.filter(
        cart=cart,
        product=item.product,
        variant=new_variant
    ).exclude(id=item.id).first()

    if existing_item:
        
        total_qty = existing_item.quantity + item.quantity
        existing_item.quantity = min(total_qty, 10)
        existing_item.save()
        item.delete()
    else:
        item.variant = new_variant
        item.save()

    return JsonResponse({"success": True,"merged": bool(existing_item),"new_item_id": existing_item.id if existing_item else item.id,"quantity": existing_item.quantity if existing_item else item.quantity,})

@login_required(login_url="login")
def cart_fragment(request):
    cart_items = []
    subtotal = 0
    has_invalid_items = False

    cart = getattr(request.user, "cart", None)

    if cart:
        for item in cart.items.select_related(
            "product", "variant", "product__category"
        ):
            product = item.product
            variant = item.variant

            is_invalid = (
                not product.is_active or
                not product.category.is_active or
                not variant.is_active or
                variant.stock <= 0
            )

            if not is_invalid:
                subtotal += product.base_price * item.quantity

            cart_items.append({
                "item": item,
                "product": product,
                "variant": variant,
                "is_invalid": is_invalid,
                "line_total": product.base_price * item.quantity if not is_invalid else 0
            })

    return render(request, "cart/_cart_items.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "has_invalid_items": has_invalid_items,
    })


@require_POST
@login_required(login_url="login")
def remove_from_cart(request, item_id):
    cart = getattr(request.user, "cart", None)
    if not cart:
        return JsonResponse({"success": False})

    item = CartItem.objects.filter(id=item_id, cart=cart).first()
    if not item:
        return JsonResponse({"success": False})

    item.delete()

   
    cart_count = sum(i.quantity for i in cart.items.all())
    
    return JsonResponse({
        "success": True,
        "cart_count": cart_count
    })