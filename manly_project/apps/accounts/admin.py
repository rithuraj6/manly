from django.contrib import admin
from .models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "is_active",
        "is_blocked",
        "is_staff",
        "created_at",
    )
    list_filter = ("is_active", "is_blocked", "is_staff")
    search_fields = ("email",)
    ordering = ("-created_at",)
    list_per_page = 10
    
    
    actions = ["block_users", "unblock_users"]

    @admin.action(description="Block selected users")
    def block_users(self, request, queryset):
        queryset.update(is_blocked=True)

    @admin.action(description="Unblock selected users")
    def unblock_users(self, request, queryset):
        queryset.update(is_blocked=False)
    