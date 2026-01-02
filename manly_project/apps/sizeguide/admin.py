from django.contrib import admin
from .models import SizeGuide

@admin.register(SizeGuide)
class SizeGuideAdmin(admin.ModelAdmin):
    list_display = (
        "size_name",
        "chest_min",
        "chest_max",
        "shoulder_min",
        "shoulder_max",
        "is_active",
    )
