from django.urls import path
from . import views
from .views import (
    user_login, user_signup,
    forgot_password, verify_otp, reset_password,
    resend_otp, user_logout ,verify_email_change ,change_password
)

from . import views


urlpatterns =[
    path("login/", user_login, name="login"),
    path("signup/", user_signup, name="signup"),

    path("resend-otp/", resend_otp, name="resend_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),

    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),
    path("change-password/", change_password, name="change_password"),

    path("logout/", user_logout, name="logout"),
    path("verify-email-change/", verify_email_change, name="verify_email_change"),


    path("profile/", views.profile_view, name="account_profile"),
    path("profile/edit/", views.profile_edit, name="account_profile_edit"),

    
    path("addresses/", views.address, name="account_addresses"),
    path("addresses/add/", views.address_add, name="account_address_add"),
    path("addresses/<int:address_id>/edit/", views.address_edit, name="account_address_edit"),
    path("addresses/<int:address_id>/delete/", views.address_delete, name="account_address_delete"),

    path("orders/", views.orders, name="account_orders"),
   
    
]

    
