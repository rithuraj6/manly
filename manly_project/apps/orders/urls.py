from django.urls import path

from .views.checkout_views import checkout_page
from .views.payment_views import (
    payment_page,
    order_failure,
    retry_payment,
    create_razorpay_order,
    verify_razorpay_payment,
    wallet_payment,
    cod_payment,
)
from .views.order_views import place_order
from .views.success_views import order_success
from .views.order_action_views import cancel_order_item
from .views.return_views import request_return, view_return_reason
from .views.invoice_views import print_invoice, order_invoice
from .views.order_list_views import user_orders
from .views.order_detail_views import order_detail
from  apps.coupons.views import apply_coupon, remove_coupon


urlpatterns = [
    path("checkout/", checkout_page, name="checkout_page"),
    path("payment/", payment_page, name="payment_page"),
    path("place-order/", place_order, name="place_order"),
    path("success/<str:order_id>/", order_success, name="order_success"),
    path("", user_orders, name="user_orders"),
    path("<str:order_id>/", order_detail, name="order_detail"),
    
    
    path("<str:order_id>/invoice/", print_invoice, name="print_invoice"),
    path("<str:order_id>/invoice/", order_invoice, name="order_invoice"),
    path("item/<int:item_id>/return/",request_return,name="return_order_item"),
    
    path("item/<int:item_id>/cancel/", cancel_order_item, name="cancel_order_item"),
    path("item/<int:item_id>/return/reason/",view_return_reason,name="view_return_reason"),
    
    path("failure/<int:payment_id>/", order_failure, name="order_failure"),
    path("retry-payment/<int:payment_id>/", retry_payment, name="retry_payment"),

    
    path("razorpay/create/", create_razorpay_order, name="create_razorpay_order"),
    path("razorpay/verify/", verify_razorpay_payment, name="verify_razorpay_payment"),

    path("payment/wallet/", wallet_payment, name="wallet_payment"),
    path("payment/cod/", cod_payment, name="cod_payment"),
    
    
    
    path("coupon/apply/", apply_coupon, name="apply_coupon"),
    path("coupon/remove/", remove_coupon, name="remove_coupon"),

    
    
    
]
