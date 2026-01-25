from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.contrib import messages
from apps.accounts.models import UserAddress
from apps.cart.models import Cart
from apps.orders.utils.pricing import apply_offer
from django.urls import reverse
from apps.orders.services.get_order_preview import get_order_preview
from django.utils.timezone import now

from apps.coupons.models import Coupon ,CouponUsage
from apps.coupons.utils.pricing import calculate_coupon_discount



@login_required
def checkout_page(request):
    user = request.user 
    cart = getattr(request.user, "cart", None)
  

    if not cart or not cart.items.exists():
        return redirect("cart_page")

    for item in cart.items.select_related("variant", "product"):
        if item.quantity > 10:
            messages.error(
                request,
                f"{item.product.name} exceeds max allowed quantity (10)."
            )
            return redirect("cart_page")

        if item.quantity > item.variant.stock:
            messages.error(
                request,
                f"{item.product.name} stock reduced. Please update cart."
            )
            return redirect("cart_page")

    if request.method == "POST":
        address_id = request.POST.get("address_id")

        if not address_id:
            messages.error(request, "Please select an address")
            return redirect("checkout_page")

    
        if address_id == "temporary":
            required_fields = [
                "full_name", "phone", "house_name",
                "street", "city", "state", "country", "pincode"
            ]

            if not all(request.POST.get(f) for f in required_fields):
                messages.error(request, "Please fill all address fields")
                return redirect("checkout_page")

            address_snapshot = {
                "full_name": request.POST["full_name"],
                "phone": request.POST["phone"],
                "house_name": request.POST["house_name"],
                "street": request.POST["street"],
                "land_mark": request.POST.get("land_mark", ""),
                "city": request.POST["city"],
                "state": request.POST["state"],
                "country": request.POST["country"],
                "pincode": request.POST["pincode"],
            }

      
        else:
            address = get_object_or_404(
                UserAddress, id=address_id, user=request.user
            )

            address_snapshot = {
                "full_name": address.full_name,
                "phone": address.phone,
                "house_name": address.house_name,
                "street": address.street,
                "land_mark": address.land_mark,
                "city": address.city,
                "state": address.state,
                "country": address.country,
                "pincode": address.pincode,
            }

        request.session["checkout_address_snapshot"] = address_snapshot
        request.session.modified = True
        return redirect("payment_page")

    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by("-is_default", "-id")

   
    preview = get_order_preview(request)

    used_coupon_ids = CouponUsage.objects.filter(
        user=user
    ).values_list("coupon_id", flat=True)

    eligible_coupons = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=now().date(),
        valid_to__gte=now().date()
    ).exclude(
        id__in=used_coupon_ids
    )

    applied_coupon_id = request.session.get("applied_coupon_id")
    if applied_coupon_id:
        eligible_coupons = eligible_coupons.exclude(id=applied_coupon_id)
    breadcrumbs = [
    {"label": "Home", "url": reverse("home")},
    {"label": "Cart", "url": reverse("cart_page")},
    {"label": "Checkout", "url": None},
    ]

    context = {
         "breadcrumbs": breadcrumbs,
        "addresses": addresses,
        "subtotal": preview["subtotal"],
        "coupon_discount": preview["coupon_discount"],
        "delivery_fee": preview["delivery_fee"],
        "tax": preview["tax"],
        "total_amount": preview["total_amount"],
         "coupon": preview.get("coupon"),
        "eligible_coupons": eligible_coupons,
    }

    return render(request, "orders/checkout.html", context)
