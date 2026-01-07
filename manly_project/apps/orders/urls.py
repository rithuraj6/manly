from django.urls import path

from .views.checkout_views import checkout_page
from .views.payment_views import payment_page
from .views.order_views import place_order 
from .views.success_views import order_success
from apps.orders.views.order_list_views import user_orders

urlpatterns = [
    path("checkout/", checkout_page, name="checkout_page"),
    path("payment/", payment_page, name="payment_page"),
    path("place-order/", place_order, name="place_order"),
    path("success/<str:order_id>/", order_success, name="order_success"),
    path("", user_orders, name="user_orders"),
]
