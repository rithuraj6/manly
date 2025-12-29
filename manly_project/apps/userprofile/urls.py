from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile_view, name="account_profile"),
    path("profile/edit/", views.profile_edit, name="account_profile_edit"),

    path("address/", views.address, name="account_address"),
    path("orders/", views.orders, name="account_orders"),
    path("password/", views.password_change, name="account_password"),
    path("logout/", views.account_logout, name="account_logout"),
]
