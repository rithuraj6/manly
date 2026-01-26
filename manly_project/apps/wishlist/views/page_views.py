
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.products.utils import attach_offer_data


@login_required(login_url="login")
def wishlist_page(request):
    wishlist = getattr(request.user, "wishlist", None)
    items = []

    if wishlist:
        qs = (
            wishlist.items
            .select_related("product", "product__category")
            .prefetch_related("product__variants", "product__images")
        )

        products = [wi.product for wi in qs]
        attach_offer_data(products)

        for wi in qs:
            product = wi.product

            is_invalid = (
                not product.is_active or
                not product.category.is_active
            )

            items.append({
                "wishlist_item": wi,
                "product": product,
                "image": product.images.first(),
                "variants": product.variants.filter(is_active=True),
                "base_price": product.base_price,
                "discounted_price": product.discounted_price,
                "offer_percentage": product.offer_percentage,
                "is_invalid": is_invalid,
            })

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Wishlist", "url": None},
    ]

    return render(request, "wishlist/wishlist.html", {
        "items": items,
        "breadcrumbs": breadcrumbs,
    })
