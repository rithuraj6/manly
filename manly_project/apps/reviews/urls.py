from django.urls import path
from apps.reviews.views import rate_product

urlpatterns = [
    path("rate/<int:item_id>/",rate_product,name="rate_product"),
]
