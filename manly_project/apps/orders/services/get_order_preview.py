from decimal import Decimal
from apps.orders.utils.pricing import apply_offer
from apps.coupons.models import Coupon
from apps.coupons.utils.pricing import calculate_coupon_discount
from apps.cart.models import Cart


def get_order_preview(request):
    user = request.user
    cart = getattr(user, "cart", None)
    applied_coupon = None


    if not cart or not cart.items.exists():
        return {
            "subtotal": Decimal("0.00"),
            "coupon_discount": Decimal("0.00"),
            "delivery_fee": Decimal("0.00"),
            "tax": Decimal("0.00"),
            "total_amount": Decimal("0.00"),
        }

    subtotal = Decimal("0.00")

    for item in cart.items.select_related("product", "variant"):
        price = apply_offer(item.product, item.product.base_price)
        subtotal += price * item.quantity

    coupon_discount = Decimal("0.00")
    coupon_id = request.session.get("applied_coupon_id")

    if coupon_id:
        
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            coupon_discount = calculate_coupon_discount(
                coupon=coupon,
                subtotal=subtotal
            )

           
            if coupon_discount <= 0:
                request.session.pop("applied_coupon_id", None)
                request.session.pop("coupon_discount", None)
            else:
                request.session["coupon_discount"] = str(coupon_discount)
                applied_coupon = coupon 

        except Coupon.DoesNotExist:
            request.session.pop("applied_coupon_id", None)
            request.session.pop("coupon_discount", None)

    delivery_fee = Decimal("0.00") if subtotal >= 3000 else Decimal("150.00")
    tax = ((subtotal - coupon_discount + delivery_fee) * Decimal("0.18")).quantize(
        Decimal("0.01")
    )

    total = subtotal - coupon_discount + delivery_fee + tax

    return {
        "subtotal": subtotal,
        "coupon_discount": coupon_discount,
        "delivery_fee": delivery_fee,
        "tax": tax,
        "total_amount": total,
          "coupon": applied_coupon,
    }
