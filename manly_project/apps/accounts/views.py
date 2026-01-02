from .utils import send_otp

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.contrib import messages
from django.utils.crypto import get_random_string




User = get_user_model()


def user_login(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                error = "Please verify your account"
            else:
                login(request, user)
                return redirect("home")
        else:
            error = "Invalid email or password"

    return render(request, "pages/login.html", {"error": error})


def user_signup(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            error = "Passwords do not match"
        else:
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                if not existing_user.is_active:
                    send_otp(existing_user, purpose="signup")
                    request.session["otp_purpose"] = "signup"
                    request.session["otp_email"] = existing_user.email
                    request.session["otp_user"] = existing_user.id
                    return redirect("verify_otp")
                else:
                    error = "Email already registered"
            else:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    is_active=False
                )
                send_otp(user, purpose="signup")
                request.session["otp_purpose"] = "signup"
                request.session["otp_email"] = user.email
                request.session["otp_user"] = user.id
                return redirect("verify_otp")

    return render(request, "pages/signup.html", {"error": error})


















from .models import EmailOTP

def verify_otp(request):
    email = request.session.get("otp_email")
    purpose = request.session.get("otp_purpose")

    if not email or not purpose:
        return redirect("login")

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()

        otp_obj = EmailOTP.objects.filter(
            email=email,
            otp=otp,
            purpose=purpose
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return render(request, "pages/verify_otp.html", {
                "error": "Invalid or expired OTP"
            })

        if purpose == "signup":
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            request.session.flush()
            messages.success(request, "Account verified. Please login.")
            return redirect("login")

        if purpose == "reset":
            request.session["reset_verified"] = True
            return redirect("reset_password")

    return render(request, "pages/verify_otp.html")


def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("otp_email")
        purpose = request.session.get("otp_purpose")

        if not email or not purpose:
            return JsonResponse({"success": False})

        user = User.objects.get(email=email)
        send_otp(user, purpose=purpose)

        return JsonResponse({"success": True})
    
    

User = get_user_model()

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "pages/forgot_password.html", {
                "error": "Account not found"
            })

        send_otp(user, purpose="reset")

        request.session["otp_purpose"] = "reset"
        request.session["otp_email"] = email

        return redirect("verify_otp")

    return render(request, "pages/forgot_password.html")

User = get_user_model()

def reset_password(request):
    if not request.session.get("reset_verified"):
        return redirect("forgot_password")

    email = request.session.get("otp_email")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            return render(request, "pages/reset_password.html", {
                "error": "Passwords do not match"
            })

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        request.session.flush()
        messages.success(request, "Password updated successfully")
        return redirect("login")

    return render(request, "pages/reset_password.html")



def user_logout(request):
    logout(request)
    return redirect("login")
