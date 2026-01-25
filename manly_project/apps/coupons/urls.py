from django.urls import path
from .views import apply_coupon, remove_coupon

urlpatterns = [
    path("apply/", apply_coupon, name="apply_coupon"),
    path("remove/", remove_coupon, name="remove_coupon"),
]
