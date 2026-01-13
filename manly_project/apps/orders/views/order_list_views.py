from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from apps.orders.models import Order, OrderItem

from apps.orders.models import Order



@login_required
def user_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by("-created_at")


    search_query = request.GET.get("q", "").strip()
    if search_query:
        matching_order_ids = (
            OrderItem.objects
            .filter(
                Q(order__user=user) &
                (
                    Q(product__name__icontains=search_query) |
                    Q(product__description__icontains=search_query)
                )
            )
            .values_list("order_id", flat=True)
        )


        orders = orders.filter(id__in=matching_order_ids).distinct()

  
    
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

   
    paginator = Paginator(orders, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    
    start_year = user.created_at.year
    current_year = now.year
    years = list(range(start_year, current_year + 1))

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "My Account", "url": "/accounts/profile/"},
        {"label": "My Orders", "url": None},
    ]

    context = {
        "orders": page_obj,
        "filter_value": filter_value,
        "years": years,
        "search_query": search_query,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "orders/order_list.html", context)
