from apps.accounts.decorators import user_required
from django.shortcuts import redirect
from django.contrib import messages
from decimal import Decimal

from apps.coupons.models import Coupon,CouponUsage
from apps.coupons.utils.pricing import calculate_coupon_discount
from apps.cart.models import Cart
from apps.orders.utils.pricing import apply_offer



@user_required
def apply_coupon(request):
    if request.method != "POST":
        return redirect("checkout_page")

    code = request.POST.get("coupon_code", "").strip().upper()

    if not code:
        messages.error(request, "Please enter a coupon code")
        return redirect("checkout_page")

  
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid or inactive coupon")
        return redirect("checkout_page")

    if CouponUsage.objects.filter(user=request.user, coupon=coupon).exists():
        messages.error(request, "You have already used this coupon")
        return redirect("checkout_page")

    cart = getattr(request.user, "cart", None)
    if not cart or not cart.items.exists():
        messages.error(request, "Cart is empty")
        return redirect("checkout_page")

    subtotal = Decimal("0.00")

    for item in cart.items.select_related("product", "variant", "product__category"):
        if (
            not item.product.is_active or
            not item.product.category.is_active or
            not item.variant.is_active or
            item.variant.stock <= 0
        ):
            messages.error(request, "Coupon cannot be applied to invalid items")
            return redirect("checkout_page")

        discounted_price = apply_offer(item.product, item.product.base_price)
        subtotal += discounted_price * item.quantity

    discount = calculate_coupon_discount(
        coupon=coupon,
        subtotal=subtotal
    )

    if discount <= 0:
        messages.error(request, "Coupon not applicable for this order")
        return redirect("checkout_page")

 
    request.session["applied_coupon_id"] = coupon.id
    request.session["coupon_discount"] = str(discount)
    request.session.modified = True

    messages.success(request, f"Coupon '{coupon.code}' applied successfully")
    return redirect("checkout_page")

@user_required
def remove_coupon(request):
    request.session.pop("applied_coupon_id", None)
    request.session.pop("coupon_discount", None)
    request.session.modified = True

    messages.success(request, "Coupon removed")
    return redirect("checkout_page")
