from django.urls import path
from .views import user_login, user_signup ,google_auth,forgot_password


urlpatterns =[
    
    # path("signup/",views.signup_request, name='signup'),
    # path('verify-otp/',views.verfiy_otp_view, name='verfiy_otp'),
    # path('login/',views.login_view,name="login"),
    # path("forgot-password/", views.forgot_password),
    # path("reset-password/", views.reset_password),
    path("login/", user_login, name="login"),
    path("signup/", user_signup, name="signup"),
    path("google/", google_auth, name="google_auth"),
    path("forgot-password/", forgot_password, name="forgot_password"),
    

    
    
    ]