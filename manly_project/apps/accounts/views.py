from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.accounts.models import User

from django.contrib.auth import authenticate, login

from apps.accounts.services.otp_service import create_or_resend_otp, verfiy_otp


# Create your views here.





@require_POST
def signup_request(request):
    
    email = request.POST.get('email')
    
    if not email:
        return JsonResponse(
            {"success ": False, "message":"Email is required"},
            status = 400,
        )
    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"success":False , "message":"Email already registered"},
            status = 400,

        )
    create_or_resend_otp(email)
    
    return JsonResponse(
        {
            "success":True , "message":"OTP sent successfully"},
        status = 200,
    )
    
    
from apps.accounts.services.otp_service import verfiy_otp

@require_POST

def verfiy_otp_view(request):
    
    email = require.POST.get('email')
    otp = request.POST.get('otp')
    password = request.POST.get('password')
    
    if not all([email,otp,password]):
        return JsonResponse (
            {"success": False ,"message":"All fields are required"},
            status = 400
        )
        
    is_valid , message = verify_otp(email,otp)
    
    if not is_valid:
        return JsonResponse(
            {"success":False , "message":message},
            status = 400,
        )
    User.objects.create_user(
        email = email,
        password = password,
        is_active = True,
    )
    
    return JsonResponse(
        {"success":True, "message":"User registered successfully"},
        status = 201,
    )
    
    
    from django.views.decorators.http import require_POST
    
@require_POST
def login_view(request):
    email = request.POST.get("email")
    password = request.POST.get("password")
    
    if not email or not passoword:
        return JsonResponse(
            {"success":False ,"message":"Email and password required"},
            status = 400,
        )
    user = authenticate(request, email= email,password= password)
    
    if user is None:
        return JsonResponse(
           {"success":False,"message":"Invalid credentials"},
            status = 401,
        )
    
    if user.is_blocked:
        return JsonResponse(
            {
                "success": False,
                "message": (
                    "Sorry, your account is temporarily blocked. "
                    "Please contact admin@manly.com"
                ),
            },
            status=403,
        
        )
    login(request,user)
    return JsonResponse(
        {"success":True ,"message":"Login successful"},
        status = 200,
    )

@require_POST
def forgot_password(request):
    email = request.POST.get("email")

    if not email:
        return JsonResponse(
            {"success": False, "message": "Email is required"},
            status=400,
        )

    if not User.objects.filter(email=email).exists():
        return JsonResponse(
            {"success": True, "message": "If email exists, OTP sent"},
            status=200,
        )

    create_or_resend_otp(email, purpose="reset")

    return JsonResponse(
        {"success": True, "message": "OTP sent for password reset"},
        status=200,
    )

    
@require_POST
def reset_password(request):
    email = request.POST.get("email")
    otp = request.POST.get("otp")
    new_password = request.POST.get("password")

    if not all([email, otp, new_password]):
        return JsonResponse(
            {"success": False, "message": "All fields are required"},
            status=400,
        )

    is_valid, message = verify_otp(email, otp, purpose="reset")

    if not is_valid:
        return JsonResponse(
            {"success": False, "message": message},
            status=400,
        )

    user = User.objects.get(email=email)
    user.set_password(new_password)
    user.save()

    return JsonResponse(
        {"success": True, "message": "Password reset successful"},
        status=200,
    )

