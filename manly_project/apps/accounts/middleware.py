from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.urls import reverse

class BlockedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        user = request.user
        path = request.path

       
        ALLOWED_PATHS = [
            reverse("login"),
            reverse("admin_login"),
            reverse("logout"),
        ]

        if (
            path.startswith("/static/")
            or path.startswith("/media/")
            or path in ALLOWED_PATHS
        ):
            return self.get_response(request)

        
        if user.is_authenticated and getattr(user, "is_blocked", False):
            logout(request)
            raise PermissionDenied

        return self.get_response(request)
