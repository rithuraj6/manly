from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfile
from apps.sizeguide.models import SizeGuide  


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(
        request,
        "account/profile_view.html",
        {"profile": profile}
    )


@login_required
def profile_edit(request):
    profile = request.user.profile

    if request.method == "POST":
        profile.first_name = request.POST.get("first_name", "").strip()
        profile.last_name = request.POST.get("last_name", "").strip()
        profile.phone = request.POST.get("phone", "").strip()

        chest = request.POST.get("chest")
        shoulder = request.POST.get("shoulder")

        profile.chest = float(chest) if chest else None
        profile.shoulder = float(shoulder) if shoulder else None

      
        profile.size = ""

        if profile.chest:
            size_match = SizeGuide.objects.filter(
                is_active=True,
                chest_min__lte=profile.chest,
                chest_max__gte=profile.chest,
            ).first()

            if size_match:
                profile.size = size_match.size_name

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect("account_profile")

    return render(
        request,
        "account/profile_edit.html",
        {"profile": profile}
    )


@login_required
def address(request):
    return render(request, "account/address.html")


@login_required
def orders(request):
    return render(request, "account/orders.html")


@login_required
def password_change(request):
    return render(request, "account/password.html")


@login_required
def account_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("login")
