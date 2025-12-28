from django.urls import path
from .views import (
    home_page,
    shop_page,
    about_page,
    contact_page,
    profile_page,
)

urlpatterns = [
    path("", home_page, name="home"),
    path("shop/", shop_page, name="shop"),
    path("about/", about_page, name="about"),
    path("contact/", contact_page, name="contact"),
    path("profile/", profile_page, name="profile"),
]
