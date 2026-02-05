from django.urls import path
from apps.reviews.views import rate_product

urlpatterns = [
    path("rate/<uuid:item_uuid>/",rate_product,name="rate_product"),
]
