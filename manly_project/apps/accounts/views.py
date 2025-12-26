from django.shortcuts import render

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.accounts.services.otp_service import create_or_resend_otp 


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

def verify_otp_view(request):
    
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
    
    
    