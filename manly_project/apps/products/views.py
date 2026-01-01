
from django.shortcuts import render,redirect

from django.http import HttpResponse
from apps.banners.models import Banner
from apps.categories.models import Category
from apps.products.models import Product
from django.db.models import Prefetch
from apps.products.models import Product, ProductImage



def shop_page(request):
    banner = Banner.objects.filter(is_active=True).order_by("-created_at").first()

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related("images").order_by("-created_at")[:8]

    categories = Category.objects.filter(
        is_active=True
    ).prefetch_related(
        Prefetch(
            "products",
            queryset=Product.objects.filter(is_active=True).prefetch_related("images")
        )
    ).order_by("-created_at")

    new_launches = Product.objects.filter(
        is_active=True
    ).prefetch_related("images").order_by("-created_at")[:12]

    context = {
        "banner": banner,
        "featured_products": featured_products,
        "categories": categories,
        "new_launches": new_launches,
    }

    return render(request, "shop/shop.html", context)




def product_detail(request, product_id):
    return HttpResponse("Product detail page – coming soon")

def product_list_by_category(request, category_id):
    return HttpResponse("Category product list – coming soon")

categories = Category.objects.filter(is_active=True).prefetch_related(
    Prefetch(
        'products',
        queryset=Product.objects.filter(is_active=True).prefetch_related('images')
    )
)
