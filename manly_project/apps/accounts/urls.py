from django.urls import path
from . import views


urlpatterns =[
    
    path("signup/",views.signup_request, name='signup'),
    path('verify-otp/',views.verfiy_otp_view, name='verfiy_otp'),
    path('login/',views.login_view,name="login"),
    path("forgot-password/", views.forgot_password),
    path("reset-password/", views.reset_password),

    
    
    ]