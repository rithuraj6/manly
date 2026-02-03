from django.core.exceptions import ValidationError
from apps.accounts.validators import name_with_spaces_validator
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from apps.categories.models import Category
from apps.accounts.decorators import admin_required






@admin_required
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

@admin_required
def admin_add_category(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        
        try:
            name_with_spaces_validator(name,field_name="Category name")
        except ValidationError as e :
            return render(request,"adminpanel/categories/category_form.html",{
                "error":e.message,
                "value":name,
            })

        if Category.objects.filter(name__iexact=name).exists():
            return render(request, "adminpanel/categories/category_form.html", {
                "error": "Category already exists",
                "value": name,
            })

        Category.objects.create(name=name)
        messages.success(request, "Category added successfully")
        return redirect("admin_category_list")

    return render(request, "adminpanel/categories/category_form.html")


@admin_required
def admin_edit_category(request, category_uuid):
    category = get_object_or_404(Category, uuid=category_uuid)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        
        try:
            name_with_spaces_validator(name,field_name="Category_name")
        except ValidationError as e :
            return render(request,"adminpanel/categories/category_form.html",{
                "error":e.message,
                "category":category ,
                
            })
            
        if Category.objects.filter(name__iexact=name).exclude(uuid=category.uuid).exists():
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
@admin_required
def admin_toggle_category_status(request, category_uuid):
    category = get_object_or_404(Category, uuid=category_uuid)
    category.is_active = not category.is_active
    category.save()

    messages.success(
        request,
        "Category activated" if category.is_active else "Category deactivated"
    )
    return redirect("admin_category_list")
