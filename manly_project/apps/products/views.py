from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import render, get_object_or_404

from apps.banners.models import SiteBanner

from apps.categories.models import Category
from apps.products.models import Product, ProductVariant, ProductImage



def shop_page(request):
    banner = SiteBanner.objects.filter(is_active=True).order_by("-created_at").first()

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

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Shop", "url": None},
    ]

    context = {
        "banner": banner,
        "featured_products": featured_products,
        "categories": categories,
        "new_launches": new_launches,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "shop/shop.html", context)




def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    product_images = ProductImage.objects.filter(product=product).order_by("id")

    variants = ProductVariant.objects.filter(
        product=product,
        is_active=True
    )

    in_stock = variants.filter(stock__gt=0).exists()

    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related("images")[:8]

    dummy_rating = {
        "rating": 4.6,
        "reviews": 486
    }

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": product.category.name, "url": f"/category/{product.category.id}/"},
        {"name": product.name, "url": None},
    ]

    context = {
        "product": product,
        "product_images": product_images,
        "variants": variants,
        "in_stock": in_stock,
        "similar_products": similar_products,
        "dummy_rating": dummy_rating,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "products/product_detail.html", context)



def product_list_by_category(request, category_id):
    base_category = get_object_or_404(Category, id=category_id, is_active=True)

    
    products = Product.objects.filter(is_active=True)

    selected_category_ids = request.GET.getlist("category")

    category_ids = [base_category.id]
    if selected_category_ids:
        category_ids.extend(selected_category_ids)

    products = products.filter(category_id__in=category_ids)

  
    search_query = request.GET.get("q", "").strip()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    
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

    products = products.prefetch_related("images", "variants").distinct()


    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Shop", "url": "/shop/"},
        {"name": base_category.name, "url": None},
    ]
    query_params = request.GET.copy()
    if "page" in query_params:
        query_params.pop("page")


    context = {
        "category": base_category,
        "categories": Category.objects.filter(is_active=True),
        "page_obj": page_obj,
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "selected_sizes": selected_sizes,
        "selected_categories": selected_category_ids or [str(base_category.id)],
        "default_size": default_size,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
        "search_query": search_query,
        "breadcrumbs": breadcrumbs,
        "query_params": query_params.urlencode(),
    }

    return render(request, "products/products_list.html", context)
