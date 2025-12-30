from django.shortcuts import render

from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.


def admin_category_list(request):
    search_query = request.GET.get("search", "").strip()

    categories = Category.objects.filter(is_deleted=False)

    # 🔍 SEARCH (case-insensitive)
    if search_query:
        categories = categories.filter(
            name__icontains=search_query
        )

    # ⬇ Latest first
    categories = categories.order_by("-created_at")

    # 📄 PAGINATION
    paginator = Paginator(categories, 5)  # 5 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }

    return render(request, "adminpanel/categories/category_list.html", context)
