from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from apps.offers.models import Offer
from apps.products.models import Product
from apps.categories.models import Category
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from apps.accounts.decorators import admin_required

from django.utils import timezone
from datetime import datetime

def make_aware_date(date_str):
    return timezone.make_aware(
        datetime.strptime(date_str, "%Y-%m-%d")
    )



@admin_required
def offer_list(request):
    
    offers = Offer.objects.select_related(
        "product","category"
        
    ).order_by('-created_at')
    
    
    return render(request,'adminpanel/offers/offer_list.html',{'offers':offers},)




@admin_required
def offer_add(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        discount_raw = request.POST.get("discount")
        product_id = request.POST.get("product")
        category_id = request.POST.get("category")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = bool(request.POST.get("is_active"))

       
        if not discount_raw:
            messages.error(request, "Discount percentage is required")
            return redirect("admin_offer_add")

        try:
            discount = int(discount_raw)
        except ValueError:
            messages.error(request, "Discount must be a number")
            return redirect("admin_offer_add")

        if discount <= 0 or discount > 90:
            messages.error(request, "Discount must be between 1 and 90")
            return redirect("admin_offer_add")

        
        if not product_id and not category_id:
            messages.error(request, "Select either a product or a category")
            return redirect("admin_offer_add")

        if product_id and category_id:
            messages.error(request, "Select only one: product OR category")
            return redirect("admin_offer_add")
        

        offer = Offer(
            name=name,
            discount_percentage=discount,
            start_date=make_aware_date(start_date),
             end_date=make_aware_date(end_date),
            is_active=is_active,
        )

        if product_id:
            offer.product_id = product_id

        if category_id:
            offer.category_id = category_id
            
        
        try:
            offer.full_clean()  
            offer.save()
        except ValidationError as e:
            messages.error(request, e.message_dict or e.messages)
            return redirect("admin_offer_add")

        messages.success(request, "Offer added successfully")
        return redirect("admin_offer_list")

    return render(
        request,
        "adminpanel/offers/offer_add.html",
        {
            "products": products,
            "categories": categories,
        }
    )
            

@require_POST
@admin_required
def toggle_offer_status(request, offer_id):
    
    offer = get_object_or_404(Offer, id=offer_id)
    now = timezone.now()
    
    
    
    if offer.end_date and offer.end_date < now:
        return JsonResponse({
            "success": False,
            "message": "Expired offers cannot be activated"
        }, status=400)

    offer.is_active = not offer.is_active
    offer.save(update_fields=["is_active"])

    messages.success(
        request,
        f"Offer {'activated' if offer.is_active else 'blocked'} successfully"
    )

    return JsonResponse({
        "success": True,
        "is_active": offer.is_active
    })
@admin_required
def offer_edit(request, offer_id):
    offer = get_object_or_404(Offer, id=offer_id)

    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        discount = int(request.POST.get("discount"))
        product_id = request.POST.get("product")
        category_id = request.POST.get("category")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = bool(request.POST.get("is_active"))

       
        if product_id and category_id:
            messages.error(request, "Select only product OR category")
            return redirect("admin_offer_edit", offer_id=offer.id)

        offer.name = name
        offer.discount_percentage = discount
        offer.start_date = start_date
        offer.end_date = end_date
        
        try:
            offer.full_clean()
            offer.save()
        except ValidationError as e:
            messages.error(request, e.message_dict or e.messages)
            return redirect("admin_offer_edit", offer_id=offer.id)
        offer.is_active = is_active
        offer.product_id = product_id or None
        offer.category_id = category_id or None

        offer.save()
        messages.success(request, "Offer updated successfully")
        return redirect("admin_offer_list")

    return render(
        request,
        "adminpanel/offers/offer_edit.html",
        {
            "offer": offer,
            "products": products,
            "categories": categories,
        }
    )



@admin_required
def offer_list(request):
    now = timezone.now()

    offers = Offer.objects.select_related(
        "product", "category"
    ).order_by("-created_at")

    for offer in offers:
        if offer.end_date and offer.end_date < now:
            offer.status = "expired"
        elif offer.is_active:
            offer.status = "active"
        else:
            offer.status = "inactive"

    return render(
        request,
        "adminpanel/offers/offer_list.html",
        {"offers": offers}
    )