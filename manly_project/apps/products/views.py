from django.core.paginator import Paginator
from django.http import HttpResponse
from apps.banners.models import Banner
from apps.categories.models import Category
from apps.products.models import Product, ProductVariant
from django.db.models import Prefetch
from apps.products.models import Product, ProductImage


from django.db.models import Q
from django.shortcuts import render, get_object_or_404

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
    base_category = get_object_or_404(Category, id=category_id, is_active=True)

    products = Product.objects.filter(
        is_active=True,
        category=base_category
    ).prefetch_related(
        "images",
        "variants"
    ).distinct()

 
  
    default_size = None
    if request.user.is_authenticated and getattr(request.user, "has_measurement", False):
        if hasattr(request.user, "measurement"):
            default_size = request.user.measurement.mapped_size

    
    selected_sizes = request.GET.getlist("size")

   
    if not selected_sizes and default_size:
        selected_sizes = [default_size]

    if selected_sizes:
        products = products.filter(
            variants__size__in=selected_sizes,
            variants__is_active=True,
            variants__stock__gt=0
        )

   
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)


  
    selected_category_ids = request.GET.getlist("category")
    if selected_category_ids:
        products = products.filter(category_id__in=selected_category_ids)

   
  

    sort = request.GET.get("sort")
    if sort == "price_low":
        products = products.order_by("base_price")
    elif sort == "price_high":
        products = products.order_by("-base_price")
    elif sort == "name_asc":
        products = products.order_by("name")
    elif sort == "name_desc":
        products = products.order_by("-name")
    else:
        products = products.order_by("-created_at")



    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "category": base_category,
        "categories": Category.objects.filter(is_active=True),
        "page_obj": page_obj,
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "selected_sizes": selected_sizes,
        "default_size": default_size,
        "selected_categories": selected_category_ids or [str(base_category.id)],
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
    }

    return render(request, "products/products_list.html", context)