from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from apps.categories.models import Category
from apps.products.models import Product

User = get_user_model()

@login_required(login_url='admin_login')
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')

    return render(request, 'adminpanel/dashboard/dashboard.html')
