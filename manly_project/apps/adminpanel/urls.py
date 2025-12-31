from django.urls import path

from .views.auth_views import admin_login, admin_logout
from .views.dashboard_views import admin_dashboard
from .views.user_views import admin_users, toggle_user_status
from .views.category_views import (
    admin_category_list,
    admin_add_category,
    admin_edit_category,
    admin_toggle_category_status,
    
)
from .views.product_views import (
    admin_product_list,
    admin_edit_product,
    admin_add_variant,
    admin_toggle_variant,
    admin_add_product,
    admin_update_variant,
    admin_toggle_product,
    admin_delete_product_image,
    admin_upload_product_image,
)


urlpatterns = [
    path("login/", admin_login, name="admin_login"),
    path("logout/", admin_logout, name="admin_logout"),

    path("dashboard/", admin_dashboard, name="admin_dashboard"),

    # USERS
    path("users/", admin_users, name="admin_users"),
    path("users/toggle/<int:user_id>/", toggle_user_status, name="toggle_user"),

    # CATEGORIES
    path("categories/", admin_category_list, name="admin_category_list"),
    path("categories/add/", admin_add_category, name="admin_add_category"),
    path("categories/edit/<int:category_id>/", admin_edit_category, name="admin_edit_category"),
    path("categories/toggle/<int:category_id>/", admin_toggle_category_status, name="admin_toggle_category"),
    
    
    # # VARIANTS
    path("products/", admin_product_list, name="admin_product_list"),
    path("products/edit/<int:product_id>/", admin_edit_product, name="admin_edit_product"),
    path("products/<int:product_id>/variants/add/", admin_add_variant, name="admin_add_variant"),
    path("variants/toggle/<int:variant_id>/", admin_toggle_variant, name="admin_toggle_variant"),
    path("products/add/", admin_add_product, name="admin_add_product"),
    path("variants/update/<int:variant_id>/", admin_update_variant, name="admin_update_variant"),
    path("products/toggle/<int:product_id>/", admin_toggle_product, name="admin_toggle_product"),
   path(
    "products/<int:product_id>/images/upload/",
    admin_upload_product_image,
    name="admin_upload_product_image"
),

path(
    "products/images/delete/<int:image_id>/",
    admin_delete_product_image,
    name="admin_delete_product_image"
),


    
]
