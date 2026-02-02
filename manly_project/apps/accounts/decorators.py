from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if  request.user.is_superuser:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("admin_login")

        if not request.user.is_staff and not request.user.is_superuser:
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return _wrapped_view
