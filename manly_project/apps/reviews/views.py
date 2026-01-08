from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from apps.orders.models import OrderItem
from apps.reviews.models import ProductReview


@login_required
def rate_product(request, item_id):
    order_item = get_object_or_404(
        OrderItem,
        id=item_id,
        order__user=request.user,
        status="delivered"
    )

    product = order_item.product

    review, created = ProductReview.objects.get_or_create(
        user=request.user,
        product=product
    )

    if request.method == "POST":
        rating = request.POST.get("rating")
        review.rating = int(float(rating))
        review.review_text = request.POST.get("review_text")
        review.save()

        return redirect(
            "order_detail",
            order_id=order_item.order.order_id
        )

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "My Orders", "url": reverse("user_orders")},
        {
            "label": f"Order {order_item.order.order_id}",
            "url": reverse("order_detail", args=[order_item.order.order_id]),
        },
        {
            "label": "Edit Review" if not created else "Rate Product",
            "url": None,
        },
    ]

    context = {
        "order_item": order_item,
        "product": product,
        "review": review,
        "is_edit": not created,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "reviews/rate_product.html", context)
