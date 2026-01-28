from django.shortcuts import get_object_or_404, redirect, render
from apps.accounts.decorators import user_required
from django.contrib import messages

from apps.orders.models import OrderItem
from apps.reviews.models import ProductReview


@user_required
def rate_product(request, item_id):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status="delivered"
    )

    
    if ProductReview.objects.filter(
        user=request.user,
        product=order_item.product
    ).exists():
        messages.warning(request, "You have already reviewed this product.")
        return redirect("order_detail", order_id=order_item.order.order_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        review_text = request.POST.get("review", "").strip()

       
        if not rating:
            messages.error(request, "Please select a rating.")
            return render(
                request,
                "reviews/rate_product.html",
                {"order_item": order_item}
            )

        ProductReview.objects.create(
            user=request.user,
            product=order_item.product,
            rating=int(rating),
            review_text=review_text
        )

        messages.success(request, "Thank you for your review!")
        return redirect("order_detail", order_id=order_item.order.order_id)

    return render(request,"reviews/rate_product.html",{"order_item": order_item})
