from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.accounts.decorators import admin_required

from apps.products.models import Product, ProductVariant

@admin_required
def admin_add_variant(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        size = request.POST.get("size")
        stock = request.POST.get("stock", 0)

        if ProductVariant.objects.filter(product=product, size=size).exists():
            messages.error(request, "Variant with this size already exists")
            return redirect("admin_edit_product", product_id=product.id)

        ProductVariant.objects.create(
            product=product,
            size=size,
            stock=stock
        )

        messages.success(request, "Variant added successfully")
        return redirect("admin_edit_product", product_id=product.id)

@admin_required
def admin_toggle_variant(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.is_active = not variant.is_active
    variant.save()

    messages.success(request, "Variant status updated")
    return redirect("admin_edit_product", product_id=variant.product.id)
