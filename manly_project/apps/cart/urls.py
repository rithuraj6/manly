from django.urls import path
from .views.cart_views import cart_page
from .views.ajax_views import add_to_cart ,remove_from_cart,update_cart_qty ,change_cart_variant,cart_fragment

urlpatterns = [
    path("", cart_page, name="cart_page"),
    path("add/", add_to_cart, name="add_to_cart"),
    path("update-qty/", update_cart_qty, name="update_cart_qty"),
    path("change-variant/", change_cart_variant, name="change_cart_variant"),
    path("fragment/", cart_fragment, name="cart_fragment"),



    
        path("remove/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
]
