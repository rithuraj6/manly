from django.urls import path
from . import views


urlpatterns =[
    
    path("signup/",views.signup_request, name='signup'),
    path('verify-otp/',views.verify_otp_view, name='verify_otp'),
    
    ]