from django.urls import path
from .views import *

urlpatterns = [
    path("", wishlist_view, name="wishlist"),
    path("add/<int:product_id>/", add_to_wishlist, name="add_to_wishlist"),
    path("remove/<int:product_id>/", remove_from_wishlist, name="remove_from_wishlist"),
]
