from django.contrib import admin

from django.contrib import admin
from .models import Product,ProductImage



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # show 3 image fields by default
    min_num = 3
    validate_min = True
    
    
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
    
    inlines = [ProductImageInline]



    actions = ["soft_delete", "restore"]

    @admin.action(description="Soft delete selected products")
    def soft_delete(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Restore selected products")
    def restore(self, request, queryset):
        queryset.update(is_active=True)
