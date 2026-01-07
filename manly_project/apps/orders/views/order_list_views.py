from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator

from apps.orders.models import Order


@login_required
def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-created_at")

    filter_value = request.GET.get("filter", "6m")
    now = timezone.now()

    if filter_value == "7d":
        orders = orders.filter(created_at__gte=now - timedelta(days=7))

    elif filter_value == "1m":
        orders = orders.filter(created_at__gte=now - timedelta(days=30))

    elif filter_value == "3m":
        orders = orders.filter(created_at__gte=now - timedelta(days=90))

    elif filter_value == "6m":
        orders = orders.filter(created_at__gte=now - timedelta(days=180))

    elif filter_value.isdigit():
        orders = orders.filter(created_at__year=int(filter_value))

    # Pagination
    paginator = Paginator(orders, 5)  # 5 orders per page (Figma-like)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Year dropdown logic
    start_year = user.created_at.year
    current_year = now.year
    years = list(range(start_year, current_year + 1))

    context = {
        "orders": page_obj,
        "filter_value": filter_value,
        "years": years,
    }

    return render(request, "orders/order_list.html", context)
