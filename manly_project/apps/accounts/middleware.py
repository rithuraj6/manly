from django.shortcuts import redirect
from django.http import HttpResponseForbidden


class BlockedUserMiddleware:


    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated and getattr(user, "is_blocked", False):
            return HttpResponseForbidden(
                "Sorry, your account is temporarily blocked. "
                "Please contact admin@manly.com"
            )

        return self.get_response(request)
