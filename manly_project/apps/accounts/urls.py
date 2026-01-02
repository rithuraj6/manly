from django.urls import path
from .views import (
    user_login, user_signup,
    forgot_password, verify_otp, reset_password,
    resend_otp, user_logout
)


urlpatterns =[
    
    path("login/", user_login, name="login"),
    path("signup/", user_signup, name="signup"),
    
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("verify-otp/", verify_otp, name="verify_otp"),

    
    
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),
    
    path("logout/", user_logout, name="logout"),

    

    ]