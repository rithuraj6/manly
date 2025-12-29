from django.urls import path
from .views.auth_views import admin_login, admin_logout
from .views.dashboard_views import admin_dashboard
from .views.user_views import admin_users, toggle_user_status


urlpatterns = [
    path('login/', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('users/', admin_users, name='admin_users'),
    path('users/toggle/<int:user_id>/', toggle_user_status, name='toggle_user'),

]


