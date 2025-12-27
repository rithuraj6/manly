from django.shortcuts import render
from django.contrib.auth import get_user_model 

# from django.http import JsonResponse
# from django.views.decorators.http import require_POST

# from apps.accounts.models import User

# from django.contrib.auth import authenticate, login

# from apps.accounts.services.otp_service import create_or_resend_otp, verfiy_otp


# # Create your views here.





# @require_POST
# def signup_request(request):
    
#     email = request.POST.get('email')
    
#     if not email:
#         return JsonResponse(
#             {"success ": False, "message":"Email is required"},
#             status = 400,
#         )
#     if User.objects.filter(email=email).exists():
#         return JsonResponse(
#             {"success":False , "message":"Email already registered"},
#             status = 400,

#         )
#     create_or_resend_otp(email)
    
#     return JsonResponse(
#         {
#             "success":True , "message":"OTP sent successfully"},
#         status = 200,
#     )
    
    
# from apps.accounts.services.otp_service import verfiy_otp

# @require_POST
# def verfiy_otp_view(request):
    
#     email = require.POST.get('email')
#     otp = request.POST.get('otp')
#     password = request.POST.get('password')
    
#     if not all([email,otp,password]):
#         return JsonResponse (
#             {"success": False ,"message":"All fields are required"},
#             status = 400
#         )
        
#     is_valid , message = verify_otp(email,otp)
    
#     if not is_valid:
#         return JsonResponse(
#             {"success":False , "message":message},
#             status = 400,
#         )
#     User.objects.create_user(
#         email = email,
#         password = password,
#         is_active = True,
#     )
    
#     return JsonResponse(
#         {"success":True, "message":"User registered successfully"},
#         status = 201,
#     )
    
    
#     from django.views.decorators.http import require_POST
    
# @require_POST
# def login_view(request):
#     email = request.POST.get("email")
#     password = request.POST.get("password")
    
#     if not email or not passoword:
#         return JsonResponse(
#             {"success":False ,"message":"Email and password required"},
#             status = 400,
#         )
#     user = authenticate(request, email= email,password= password)
    
#     if user is None:
#         return JsonResponse(
#            {"success":False,"message":"Invalid credentials"},
#             status = 401,
#         )
    
#     if user.is_blocked:
#         return JsonResponse(
#             {
#                 "success": False,
#                 "message": (
#                     "Sorry, your account is temporarily blocked. "
#                     "Please contact admin@manly.com"
#                 ),
#             },
#             status=403,
        
#         )
#     login(request,user)
#     return JsonResponse(
#         {"success":True ,"message":"Login successful"},
#         status = 200,
#     )

# @require_POST
# def forgot_password(request):
#     email = request.POST.get("email")

#     if not email:
#         return JsonResponse(
#             {"success": False, "message": "Email is required"},
#             status=400,
#         )

#     if not User.objects.filter(email=email).exists():
#         return JsonResponse(
#             {"success": True, "message": "If email exists, OTP sent"},
#             status=200,
#         )

#     create_or_resend_otp(email, purpose="reset")

#     return JsonResponse(
#         {"success": True, "message": "OTP sent for password reset"},
#         status=200,
#     )

    
# @require_POST
# def reset_password(request):
#     email = request.POST.get("email")
#     otp = request.POST.get("otp")
#     new_password = request.POST.get("password")

#     if not all([email, otp, new_password]):
#         return JsonResponse(
#             {"success": False, "message": "All fields are required"},
#             status=400,
#         )

#     is_valid, message = verify_otp(email, otp, purpose="reset")

#     if not is_valid:
#         return JsonResponse(
#             {"success": False, "message": message},
#             status=400,
#         )

#     user = User.objects.get(email=email)
#     user.set_password(new_password)
#     user.save()

#     return JsonResponse(
#         {"success": True, "message": "Password reset successful"},
#         status=200,
#     )


def user_login(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid email or password"

    return render(request, 'pages/login.html')



User = get_user_model()

def user_signup(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            error = "Passwords do not match"
        elif User.objects.filter(email=email).exists():
            error = "Email already registered"
        else:
            user = User.objects.create_user(
                email=email,
                password=password
            )
            # OTP trigger will come next phase
            return redirect("login")

    return render(request, "pages/signup.html", {"error": error})


def forgot_password(request):
    return render(request,"pages/forgot_password.html")


def google_auth(request):
    return redirect("login")  # placeholder
