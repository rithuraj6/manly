from django.urls import path
from .views import wallet_page


urlpatterns = [
    path("", wallet_page, name="wallet_page"),
]