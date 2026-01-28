from functools import wraps
from django.shortcuts import redirect, render


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

       
        if not request.user.is_superuser:
            return render(
                request,
                "errors/403.html",
                {
                    "title": "Access Denied",
                    "message": "This page is restricted to administrators only.",
                },
                status=403,
            )

       
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        
        if request.user.is_superuser:
            return render(
                request,
                "errors/403.html",
                {
                    "title": "Access Denied",
                    "message": "Administrators cannot access this page.",
                },
                status=403,
            )

       
        if hasattr(request.user, "profile") and request.user.profile.is_blocked:
            return render(
                request,
                "errors/403.html",
                {
                    "title": "Account Blocked",
                    "message": "Your account has been blocked. Please contact support.",
                },
                status=403,
            )

       
        return view_func(request, *args, **kwargs)

    return _wrapped_view
