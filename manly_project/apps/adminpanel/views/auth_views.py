from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages


def admin_login(request):
   
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            messages.error(request, "Invalid email or password")
            return redirect('admin_login')
        
        
        if not (user.is_staff or user.is_superuser):
            
            return render(request,"errors/403.html",{
                "title":"Access  Denied!",
                "message":"Customers must use the customer login page!"
            },status=403,
            )

        login(request, user)
        return redirect('admin_dashboard')

    return render(request, 'adminpanel/login.html')


def admin_logout(request):
    logout(request)
    return redirect('admin_login')


