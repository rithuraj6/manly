from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_page(request):
    return render(request, "pages/home.html")


def shop_page(request):
    return render(request, "pages/home.html")


def about_page(request):
    return render(request, "pages/about.html")


def contact_page(request):
    return render(request, "pages/contact.html")


@login_required(login_url="login")
def profile_page(request):
    return render(request, "pages/profile.html")
