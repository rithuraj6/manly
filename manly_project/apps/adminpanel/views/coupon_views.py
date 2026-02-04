from apps.accounts.validators import coupon_code_validator
from django.shortcuts import render, redirect, get_object_or_404
from apps.accounts.decorators import admin_required

from django.core.paginator import Paginator

from apps.coupons.models import Coupon
from datetime import datetime

from django.contrib import messages
from django.utils.dateparse import parse_datetime
from django.core.exceptions import ValidationError






@admin_required
def coupon_list(request):
    
    coupons = Coupon.objects.all().order_by("-created_at")
    
    paginator = Paginator(coupons,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context={
        
        "page_obj":page_obj,
    }
    
    return render(request,'adminpanel/coupons/coupon_list.html',context)

@admin_required
def toggle_coupon_status(request,coupon_uuid):
    coupon = get_object_or_404(Coupon,uuid=coupon_uuid)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return redirect('admin_coupon_list')



@admin_required
def add_coupon(request):
    if request.method == "POST":
        
        
        try:
            valid_from_str = request.POST.get("valid_from")
            valid_to_str = request.POST.get("valid_to")

            if not valid_from_str or not valid_to_str:
                messages.error(request, "Valid From and Valid To dates are required")
                return render(request, "adminpanel/coupons/coupon_add.html")
            
            code = request.POST.get("code","").strip().upper()
            coupon_code_validator(code)
            
            discount_type = request.POST.get("discount_type")
            discount_value = request.POST.get("discount_value")
            
            max_discount = request.POST.get("max_discount_amount")
            
            if discount_type == "FLAT":
                discount_value = max_discount  


            coupon = Coupon(
                code=code,
                discount_type=discount_type,         
                discount_value=discount_value,
                min_purchase_amount=request.POST.get("min_purchase_amount") or 0,
                max_discount_amount=request.POST.get("max_discount_amount") or None,
                valid_from=datetime.strptime(valid_from_str, "%Y-%m-%d").date(),
                valid_to=datetime.strptime(valid_to_str, "%Y-%m-%d").date(),
                is_active=True if request.POST.get("is_active") else False,
            )

            coupon.full_clean()
            coupon.save()

            messages.success(request, "Coupon added successfully")
            return redirect("admin_coupon_list")

        except ValidationError as e:
            messages.error(request, e.message)

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, "adminpanel/coupons/coupon_add.html")









@admin_required
def edit_coupon(request, coupon_uuid):
    coupon = get_object_or_404(Coupon, uuid=coupon_uuid)

    if request.method == "POST":
        try:
           
          
            coupon.min_purchase_amount = request.POST.get("min_purchase_amount") or 0
    
            coupon.is_active = True if request.POST.get("is_active") else False
            
            discount_type = request.POST.get("discount_type")
            discount_value = request.POST.get("discount_value")
            max_discount = request.POST.get("max_discount_amount")
            
            if discount_type == "FLAT":
                discount_value = max_discount
                
            coupon.discount_type = discount_type
            coupon.discount_value = discount_value
            coupon.max_discount_amount = max_discount or None
            coupon.min_purchase_amount = request.POST.get("min_purchase_amount") or 0

          
            valid_from_str = request.POST.get("valid_from")
            valid_to_str = request.POST.get("valid_to")

            if not valid_from_str or not valid_to_str:
                messages.error(request, "Valid From and Valid To dates are required")
                return render(
                    request,
                    "adminpanel/coupons/coupon_edit.html",
                    {"coupon": coupon},
                )

            coupon.valid_from = datetime.strptime(
                valid_from_str, "%Y-%m-%d"
            ).date()

            coupon.valid_to = datetime.strptime(
                valid_to_str, "%Y-%m-%d"
            ).date()

            coupon.full_clean()
            coupon.save()

            messages.success(request, "Coupon updated successfully")
            return redirect("admin_coupon_list")

        except ValidationError as e:
            messages.error(request, e.messages[0])

        except Exception as e:
           
            messages.error(request, f"Error: {e}")

    return render(
        request,
        "adminpanel/coupons/coupon_edit.html",
        {"coupon": coupon},
    )