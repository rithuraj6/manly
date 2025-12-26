from django.contrib import admin

from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "color",
        "is_active",
        "created_at",
    )

    list_filter = ("category", "is_active")
    search_fields = ("name", "color")
    ordering = ("-created_at",)
    list_per_page = 10

    actions = ["soft_delete", "restore"]

    @admin.action(description="Soft delete selected products")
    def soft_delete(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Restore selected products")
    def restore(self, request, queryset):
        queryset.update(is_active=True)
