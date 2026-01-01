from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from apps.banners.models import Banner


def admin_banner_list(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    banners = Banner.objects.all()

    return render(
        request,
        "adminpanel/banners/banner_list.html",
        {"banners": banners}
    )


def admin_add_banner(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        Banner.objects.create(
            title=request.POST.get("title"),
            subtitle=request.POST.get("subtitle"),
            image=request.FILES.get("image"),
            is_active=True,
        )

        messages.success(request, "Banner added successfully")
        return redirect("admin_banner_list")

    return render(request, "adminpanel/banners/banner_add.html")


def admin_toggle_banner(request, banner_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    banner = get_object_or_404(Banner, id=banner_id)
    banner.is_active = not banner.is_active
    banner.save()

    messages.success(request, "Banner status updated")
    return redirect("admin_banner_list")


