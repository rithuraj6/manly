from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from apps.categories.models import Category
from django.contrib.auth.decorators import login_required



@login_required(login_url='admin_login')
def admin_category_list(request):
    search_query = request.GET.get("search", "").strip()

    categories = Category.objects.all()

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    categories = categories.order_by("-created_at")

    paginator = Paginator(categories, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "adminpanel/categories/category_list.html", {
        "page_obj": page_obj,
        "search_query": search_query,
    })


@login_required(login_url='admin_login')
def admin_add_category(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if Category.objects.filter(name__iexact=name).exists():
            return render(request, "adminpanel/categories/category_form.html", {
                "error": "Category already exists",
                "value": name,
            })

        Category.objects.create(name=name)
        messages.success(request, "Category added successfully")
        return redirect("admin_category_list")

    return render(request, "adminpanel/categories/category_form.html")


@login_required(login_url='admin_login')
def admin_edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            return render(request, "adminpanel/categories/category_form.html", {
                "error": "Category already exists",
                "category": category,
            })

        category.name = name
        category.save()
        messages.success(request, "Category updated successfully")
        return redirect("admin_category_list")

    return render(request, "adminpanel/categories/category_form.html", {
        "category": category
    })
@login_required(login_url='admin_login')
def admin_toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.is_active = not category.is_active
    category.save()

    messages.success(
        request,
        "Category activated" if category.is_active else "Category deactivated"
    )
    return redirect("admin_category_list")
