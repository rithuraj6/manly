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
    
]
