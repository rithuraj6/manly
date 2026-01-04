from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.profile_view, name="account_profile"),
    path("profile/edit/", views.profile_edit, name="account_profile_edit"),

    path("addresses/", views.address, name="account_addresses"),
    path("addresses/add/", views.address_add, name="account_address_add"),
    path("addresses/<int:address_id>/edit/", views.address_edit, name="account_address_edit"),
    path("addresses/<int:address_id>/delete/",views.address_delete,name="account_address_delete"),

    


    path("orders/", views.orders, name="account_orders"),
    path("password/", views.password_change, name="account_password"),
    path("logout/", views.account_logout, name="account_logout"),
    path("profile/", views.profile_view, name="account_profile"),

]
