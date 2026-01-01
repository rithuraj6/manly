from django.contrib import admin
from .models import SiteBanner

@admin.register(SiteBanner)
class SiteBannerAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)
