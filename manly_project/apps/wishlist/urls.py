from django.urls import path
from .views import *

urlpatterns = [
    path("", wishlist_view, name="wishlist"),
    
]
