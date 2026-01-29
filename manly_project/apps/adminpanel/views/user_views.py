from apps.accounts.decorators import admin_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.db.models import Q
from apps.accounts.models import UserAddress
from django.db.models import Prefetch


User = get_user_model()


@admin_required
def admin_users(request):
    if not request.user.is_staff:
        return redirect('admin_login')

    search = request.GET.get('search', '').strip()

    users = (
        User.objects
        .exclude(email="admin@manly.com")
        .prefetch_related(
            Prefetch(
                "addresses",
                queryset=UserAddress.objects.order_by("-created_at"),
                to_attr="latest_addresses"
            )
        )
        .order_by("-id")
    )

    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(addresses__phone__icontains=search) |
            Q(addresses__full_name__icontains=search)
        ).distinct()

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
    }

    return render(request, "adminpanel/users/user_list.html", context)

# @admin_required
# def toggle_user_status(request, user_id):
#     if not request.user.is_staff:
#         return redirect('admin_login')

#     user = User.objects.get(id=user_id)
#     user.is_active = not user.is_active
#     user.save()
#     return redirect('admin_users')



@admin_required
def toggle_user_status(request,user_id):
    
    user = get_object_or_404(User,id=user_id)
    
    if user.is_superuser or user.is_staff:
        return redirect("admin_users")
    
    user.is_blocked = not user.is_blocked
    user.save(update_fields=["is_blocked"])
    
    return redirect("admin_users")

