from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model , logout
from django.http import JsonResponse

from .utils import send_otp, verify_user_otp

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
                    request.session["otp_user"] = existing_user.id
                    return redirect("verfiy_otp")
                else:
                    error = "Email already registered"
            else:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    is_active=False
                )
                send_otp(user, purpose="signup")
                request.session["otp_user"] = user.id
                return redirect("verfiy_otp")

    return render(request, "pages/signup.html", {"error": error})


def verfiy_otp(request):
    error = None
    user_id = request.session.get("otp_user")

    if not user_id:
        return redirect("signup")

    if request.method == "POST":
        otp = request.POST.get("otp")

        if verify_user_otp(user_id, otp, purpose="signup"):
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            del request.session["otp_user"]
            return redirect("login")
        else:
            error = "Invalid or expired OTP"

    return render(request, "pages/verfiy_otp.html", {"error": error})


def resend_otp(request):
    if request.method == "POST":
        user_id = request.session.get("otp_user")
        if not user_id:
            return JsonResponse({"success": False})

        user = User.objects.get(id=user_id)
        send_otp(user, purpose="signup")
        return JsonResponse({"success": True})


def forgot_password(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
            send_otp(user, purpose="reset")
            request.session["reset_user"] = user.id
            return redirect("reset_password")
        except User.DoesNotExist:
            error = "No account found with this email"

    return render(request, "pages/forgot_password.html", {"error": error})


def reset_password(request):
    error = None
    user_id = request.session.get("reset_user")

    if not user_id:
        return redirect("forgot_password")

    if request.method == "POST":
        otp = request.POST.get("otp")
        password = request.POST.get("password")

        if verify_user_otp(user_id, otp, purpose="reset"):
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            del request.session["reset_user"]
            return redirect("login")
        else:
            error = "Invalid or expired OTP"

    return render(request, "pages/reset_password.html", {"error": error})


def google_auth(request):
    return redirect("login")


def user_logout(request):
    logout(request)
    return redirect("login")
