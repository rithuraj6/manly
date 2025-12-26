from django.contrib import admin
from .models import User

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email","is_staff", "is_blocked" , "is_active", "created_at")
    list_filter = ("is_staff", "is_blocked" , "is_blocked")
    search_fields = ("email",)
    ordering = ("-created_at",)
    
    