from django.shortcuts import render

from django.core.paginator import Paginator
from django.db.models import Q
from apps.accounts.decorators import admin_required
import uuid


@admin_required
def admin_category_list(request):
    
    
    search_query = request.GET.get("search", "").strip()

    categories = Category.objects.filter(is_deleted=False)

   
    if search_query:
        categories = categories.filter(
            name__icontains=search_query
        )


    categories = categories.order_by("-created_at")

   
    paginator = Paginator(categories, 5)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
    }

    return render(request, "adminpanel/categories/category_list.html", context)
