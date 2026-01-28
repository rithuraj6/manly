from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import render, get_object_or_404,redirect
from decimal import Decimal
from apps.banners.models import SiteBanner

from apps.categories.models import Category
from apps.products.models import Product, ProductVariant, ProductImage

from django.db.models import Avg, Count
from apps.reviews.models import ProductReview

from apps.orders.utils.pricing import apply_offer, get_best_offer

from apps.products.utils import attach_offer_data


from apps.sizeguide.models import SizeGuide

def toggle_user_size(request):
    
    current = request.session.get("disable_user_size", False)
    request.session["disable_user_size"] = not current
    request.session.modified = True

    
    return redirect(request.META.get("HTTP_REFERER", "/"))


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
    is_active=True,
    is_featured=False
    ).prefetch_related("images").order_by("-created_at")[:12]
    
    
    attach_offer_data(featured_products)
    attach_offer_data(new_launches)

    for category in categories:
        attach_offer_data(category.products.all())


    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Shop", "url": None},
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

   
    similar_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .prefetch_related("images")[:8]
    )
    attach_offer_data(similar_products)

    reviews = (
    ProductReview.objects
    .filter(product=product)
    .select_related("user")
    .order_by("-created_at")    
    )


    reviews_agg = ProductReview.objects.filter(
        product=product,
        
    ).aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id")
    )

    average_rating = round(reviews_agg["avg_rating"] or 0, 1)
    total_reviews = reviews_agg["total_reviews"] or 0
    
    # offer = get_best_offer(product)

    # discounted_price = (
    #     apply_offer(product, product.base_price)
    #     if offer else product.base_price
    # )

    # offer_percentage = offer.discount_percentage if offer else None
    
    discounted_price = apply_offer(product, product.base_price)

    if discounted_price < product.base_price:
        offer_percentage = (
            (product.base_price - discounted_price)
            / product.base_price * 100
        ).quantize(Decimal("1"))
    else:
        offer_percentage = None

            

   
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": product.category.name, "url": f"/category/{product.category.id}/"},
        {"label": product.name, "url": None},
    ]

    context = {
        "product": product,
        "product_images": product_images,
        "variants": variants,
        "in_stock": in_stock,
        "similar_products": similar_products,
        "average_rating": average_rating,
           "discounted_price": discounted_price,
            "offer_percentage": offer_percentage,
        'reviews' : reviews,
        "total_reviews": total_reviews,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "products/product_detail.html", context)



def product_list_by_category(request, category_id):
    base_category = get_object_or_404(Category, id=category_id, is_active=True)
    
    

    selected_category_ids = request.GET.getlist("category")
    selected_sizes = request.GET.getlist("size")

    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    search_query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "").strip()
    
    category_ids = [base_category.id]
    wishlist_product_ids = set()

 
    
    if selected_category_ids:
        category_ids.extend([int(cid) for cid in selected_category_ids])

    products = Product.objects.filter(is_active=True,category_id__in=category_ids)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

 
   
    
    user_size = None
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        user_size = request.user.profile.size
    
    disable_user_size = request.session.get("disable_user_size", False)

    if selected_sizes:
       
        products = products.filter(
            variants__size__in=selected_sizes,
            variants__is_active=True,
            variants__stock__gt=0
        )

    elif user_size and not disable_user_size:
  
        products = products.filter(
            variants__size=user_size,
            variants__is_active=True,
            variants__stock__gt=0
        )

    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)

   
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
    
   
    products = products.distinct().prefetch_related("images", "variants")
    
    attach_offer_data(products)


  
    paginator = Paginator(products, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

   
    has_filters = any([
        bool(selected_category_ids),
        bool(selected_sizes),
        bool(min_price),
        bool(max_price),
        bool(search_query),
        bool(sort),
    ])


    query_params = request.GET.copy()
    query_params.pop("page", None)
    FILTER_KEYS = ["category", "size", "min_price", "max_price"]
    has_search = bool(search_query)
    has_sort = bool(sort)
    has_filter_only = any([
        selected_category_ids,
        selected_sizes,
        min_price,
        max_price,
    ])
 
    clean_params = request.GET.copy()
    for key in list(clean_params.keys()):
        if not clean_params.get(key):
            clean_params.pop(key)

    def build_clear_url(remove_keys):
        params = clean_params.copy()
        for key in remove_keys:
            params.pop(key, None)
        return params.urlencode()


    clear_search_url = build_clear_url(["q"])
    clear_sort_url = build_clear_url(["sort"])
    clear_filter_url = build_clear_url(FILTER_KEYS)



  
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Shop", "url": "/shop/"},
        {"label": base_category.name, "url": None},
    ]
    default_size = (
        request.user.profile.size
        if request.user.is_authenticated and hasattr(request.user, "profile")
       
       
        else None
    )
    wwishlist_product_ids = set()

    if request.user.is_authenticated:
        wishlist = getattr(request.user, "wishlist", None)
        if wishlist:
            wishlist_product_ids = set(
                wishlist.items.values_list("product_id", flat=True)
            )



 
    context = {
        "category": base_category,
        "categories": Category.objects.filter(is_active=True),
        "page_obj": page_obj,
        "sizes": SizeGuide.objects.filter(is_active=True)
        .values_list("size_name", flat=True),
        "selected_sizes": selected_sizes,
        "selected_categories": selected_category_ids or [str(base_category.id)],
        "default_size": default_size,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
        "search_query": search_query,
        "breadcrumbs": breadcrumbs,
        "wishlist_product_ids": wishlist_product_ids,
       
        "has_filters": has_filters,
            "filter_keys": FILTER_KEYS,
             "query_params": query_params.urlencode(),

         "query_params_dict": request.GET.copy(),
         "has_search": has_search,
    "has_sort": has_sort,
    "has_filter_only": has_filter_only,
     "clear_search_url": clear_search_url,
    "clear_sort_url": clear_sort_url,
    "clear_filter_url": clear_filter_url,
    "user_size": (
        request.user.profile.size
        if request.user.is_authenticated and hasattr(request.user, "profile")
        else None
    ),





        }
    
    
   

    return render(request, "products/products_list.html", context)



