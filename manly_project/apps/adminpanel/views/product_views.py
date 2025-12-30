from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from apps.products.utils import crop_and_resize
from apps.products.models import Product, ProductVariant
from apps.categories.models import Category


# =========================
# PRODUCT LIST
# =========================
def admin_product_list(request):
    search = request.GET.get("search", "").strip()

    products = Product.objects.select_related("category")

    if search:
        products = products.filter(name__icontains=search)

    products = products.order_by("-created_at")

    paginator = Paginator(products, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "adminpanel/products/product_list.html",
        {
            "page_obj": page_obj,
            "search": search,
        },
    )


# =========================
# ADD PRODUCT
# =========================
def admin_add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        product = Product.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            base_price=request.POST.get("price"),
            category_id=request.POST.get("category"),
            is_active=True,
        )

        messages.success(request, "Product created. Add variants now.")
        return redirect("admin_edit_product", product_id=product.id)

    return render(
        request,
        "adminpanel/products/product_edit.html",
        {"categories": categories},
    )


# =========================
# EDIT PRODUCT
# =========================
def admin_edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variants = product.variants.all().order_by("size")
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.base_price = request.POST.get("price")
        product.category_id = request.POST.get("category")

        if request.FILES.get("image"):
            product.image = crop_and_resize(request.FILES["image"])

        product.save()
        messages.success(request, "Product updated successfully")
        return redirect("admin_product_list")

    return render(
        request,
        "adminpanel/products/product_edit.html",
        {
            "product": product,
            "variants": variants,
            "categories": categories,
        },
    )


# =========================
# ADD VARIANT
# =========================
def admin_add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        size = request.POST.get("size")
        stock = request.POST.get("stock")

        if ProductVariant.objects.filter(product=product, size=size).exists():
            messages.error(request, "Variant already exists for this product")
            return redirect("admin_product_list")

        ProductVariant.objects.create(
            product=product,
            size=size,
            stock=stock,
            is_active=True,
        )

        messages.success(request, "Variant added successfully")
        return redirect("admin_product_list")


# =========================
# UPDATE VARIANT STOCK
# =========================
def admin_update_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == "POST":
        variant.stock = request.POST.get("stock")
        variant.save()
        messages.success(request, "Variant stock updated")

    return redirect("admin_product_list")

# =========================
# TOGGLE VARIANT
# =========================
def admin_toggle_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.is_active = not variant.is_active
    variant.save()

    messages.success(request, "Variant status updated")
    return redirect("admin_product_list")


# =========================
# TOGGLE PRODUCT
# =========================
def admin_toggle_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.is_active = not product.is_active
    product.save()

    messages.success(request, "Product status updated")
    return redirect("admin_product_list")
