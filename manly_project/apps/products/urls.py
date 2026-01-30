from django.urls import path
from .views import shop_page, product_detail, product_list_by_category,toggle_user_size

urlpatterns = [
    path("shop/", shop_page, name="shop"),

    path("product/<uuid:uuid>/", product_detail, name="product_detail"),

    path("category/<uuid:category_uuid>/", product_list_by_category, name="product_list_by_category"),
   
    path("toggle-user-size/",toggle_user_size, name="toggle_user_size"),
    
]
