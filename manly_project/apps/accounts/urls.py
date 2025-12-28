from django.urls import path
from .views import(
    user_login, user_signup ,google_auth,
    forgot_password,verfiy_otp,reset_password,
    resend_otp
)


urlpatterns =[
    
    path("login/", user_login, name="login"),
    path("signup/", user_signup, name="signup"),
    path("verfiy-otp/", verfiy_otp, name="verfiy_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/", reset_password, name="reset_password"),
    path("google/", google_auth, name="google_login"),



    
    
    ]