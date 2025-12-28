from django.urls import path
from .views import *

urlpatterns = [
    path("", cart_view, name="cart"),
    path("add/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
]
