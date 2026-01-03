from django.urls import path
from .views import *

urlpatterns = [
    path("", cart_view, name="cart"),

]
