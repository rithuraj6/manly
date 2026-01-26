

from django.urls import path
from apps.wishlist.views import ajax_views
from apps.wishlist.views.page_views import wishlist_page



urlpatterns = [
    path("", wishlist_page, name="wishlist_page"),

    path("toggle/", ajax_views.toggle_wishlist, name="toggle_wishlist"),
    path("check/", ajax_views.is_in_wishlist, name="is_in_wishlist"),
    path("remove/", ajax_views.remove_from_wishlist, name="remove_from_wishlist"),
    path("add-to-cart/", ajax_views.wishlist_add_to_cart, name="wishlist_add_to_cart"),
]