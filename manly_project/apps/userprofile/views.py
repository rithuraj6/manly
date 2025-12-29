from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import UserProfile


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(request, "account/profile_view.html", {"profile": profile})


@login_required
def profile_edit(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile.first_name = request.POST.get("first_name", "")
        profile.last_name = request.POST.get("last_name", "")
        profile.phone = request.POST.get("phone", "")
        profile.chest = request.POST.get("chest") or None
        profile.shoulder = request.POST.get("shoulder") or None
        profile.save()
        return redirect("account_profile")

    return render(request, "account/profile_edit.html", {"profile": profile})



@login_required
def address(request):
    return render(request, "account/address.html")


@login_required
def orders(request):
    return render(request, "account/orders.html")


@login_required
def password_change(request):
    return render(request, "account/password_change.html")


@login_required
def account_logout(request):
    logout(request)
    return redirect("login")
