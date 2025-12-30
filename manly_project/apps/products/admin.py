from django.contrib import admin
from .models import Product, ProductVariant


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "base_price",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "is_active")
    search_fields = ("name",)
    ordering = ("-created_at",)
    list_per_page = 10


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "stock",
        "is_active",
    )
    list_filter = ("size", "is_active")
    ordering = ("product",)
