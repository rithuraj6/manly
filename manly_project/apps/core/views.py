from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.banners.models import Banner


from django.shortcuts import render
from apps.banners.models import Banner
from apps.products.models import Product


def home_page(request):
    banner = Banner.objects.filter(is_active=True).order_by("-created_at").first()

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).prefetch_related("images")[:8]

    return render(
        request,
        "pages/home.html",
        {
            "banner": banner,
            "featured_products": featured_products,
        }
    )

def shop_page(request):
    return render(request, "pages/home.html")


def about_page(request):
    return render(request, "pages/about.html")


def contact_page(request):
    return render(request, "pages/contact.html")


@login_required(login_url="login")
def profile_page(request):
    return render(request, "account/account_base.html")


