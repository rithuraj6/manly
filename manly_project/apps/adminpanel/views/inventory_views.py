from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum ,Q
from django.core.paginator import Paginator

from apps.products.models import Category, Product, ProductVariant


@login_required(login_url="admin_login")
def inventory_category_list(request):
    categories = (
        Category.objects
        .filter(is_active=True)
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__is_active=True)
            )
        )
    )

    return render(request,"adminpanel/inventory/category_list.html",{"categories": categories})


@login_required(login_url="admin_login")
def inventory_product_list(request, category_id):
    category = get_object_or_404(Category, id=category_id, is_active=True)

    products = (
        Product.objects
        .filter(is_active=True, category=category)
        .prefetch_related("variants")
        .annotate(
            total_stock=Sum("variants__stock")
        )
        .order_by("name")
    )

    paginator = Paginator(products, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request,"adminpanel/inventory/product_list.html",{"category": category,"products": page_obj,})
