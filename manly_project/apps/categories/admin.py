from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("-created_at",)
    list_per_page = 10

    actions = ["soft_delete", "restore"]

    @admin.action(description="Soft delete selected categories")
    def soft_delete(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Restore selected categories")
    def restore(self, request, queryset):
        queryset.update(is_active=True)
