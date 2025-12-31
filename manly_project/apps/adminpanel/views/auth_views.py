from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect('admin_login')

        if not user.is_staff:
            messages.error(request, "You are not allowed to access admin panel")
            return redirect('admin_login')

        login(request, user)
        return redirect('admin_dashboard')

    return render(request, 'adminpanel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')
