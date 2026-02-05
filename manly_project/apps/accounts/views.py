from django.core.exceptions import ValidationError

from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from apps.accounts.decorators import user_required
from django.http import JsonResponse
from django.contrib import messages
from apps.accounts.models import EmailOTP
from django.core.paginator import Paginator
from apps.accounts.models import UserProfile, UserAddress
from apps.sizeguide.models import SizeGuide
from .utils import send_otp
from .validators import only_letters_validator, only_numbers_validator ,validate_email_strict ,validate_password_strict,validate_phone_number ,name_with_spaces_max10,street_field_validator
from apps.accounts.validators import (
    name_with_spaces_max10,
    alphabets_only_field,
    numbers_only_field,
)

from apps.accounts.validators import validate_measurement
from apps.accounts.services.size_mapping import calculate_user_size
from django.utils.timezone import now

from apps.coupons.models import Coupon, CouponUsage

import cloudinary.uploader
import base64


User = get_user_model()


def user_login(request):
    error =None
   

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)
        if not user:
            messages.error(request, "Invalid email or password")
            return redirect("login")
        
        if user.is_superuser or user.is_staff:
            return render(
                request,"errors/403.html",{
                    "title":"Access Denied!",
                    "message":"Admin accounts must  use the  admni login page "
                },
                status =403,
            )

        
        if user.is_blocked:
            request.session["blocked_reason"] = "account_blocked"
            return redirect("forbidden")


       
        login(request, user)
        return redirect("home")

    

    return render(request, "pages/login.html", {"error": error})

def forbidden_view(request):
    reason = request.session.pop("blocked_reason", None)

    return render(
        request,
        "errors/403.html",
        {
            "title": "Access Denied!",
            "message": "Your account has been blocked. Please contact support.",
        },
        status=403,
    )



def user_signup(request):
    error =None
    
    if request.method =="POST":
        email = request.POST.get("email","")
        password = request.POST.get("password","")
        confirm = request.POST.get("confirm_password")
        
        try:
            email = validate_email_strict(email)
            
            password = validate_password_strict(password)
            
            
            if password != confirm:
                raise ValidationError("Passwords does not match")
            
            existing_user = User.objects.filter(email= email).first()
            
            if existing_user:
                if not existing_user.is_active:
                    send_otp(existing_user,purpose="signup")
                    request.session["otp_user"]= existing_user.id 
                    
                else:
                    raise ValidationError("Email already registered")
                
            else:
                user = User.objects.create_user(
                    email=email,password=password,is_active=False
                ) 
                
                send_otp(user,purpose ="signup")
                
                request.session["otp_user"] =user.id
                
            request.session["otp_purpose"] ="signup"
            request.session["otp_email"]= email
            
            return redirect("verify_otp")
        
        
        except ValidationError as e:
            error =e.message
        except Exception:
            error ="Something went wrong. please try again!"
    return render(request,"pages/signup.html",{"error":error})
            
            
def verify_otp(request):
    email = request.session.get("otp_email")
    purpose = request.session.get("otp_purpose")

    if not email or not purpose:
        return redirect("login")

    if request.method == "POST":
        otp = request.POST.get("otp", "").strip()

        otp_obj = EmailOTP.objects.filter(
            email=email,
            otp=otp,
            purpose=purpose
        ).last()

        if not otp_obj or otp_obj.is_expired():
            return render(request, "pages/verify_otp.html", {
                "error": "Invalid or expired OTP"
            })

        if purpose == "signup":
            user = User.objects.get(email=email)
            user.is_active = True
            user.save()
            request.session.flush()
            messages.success(request, "Account verified. Please login.")
            return redirect("login")

        if purpose == "reset":
            request.session["reset_verified"] = True
            return redirect("reset_password")

    return render(request, "pages/verify_otp.html")


def resend_otp(request):
    if request.method == "POST":
        email = request.session.get("otp_email")
        purpose = request.session.get("otp_purpose")

        try:
            user = User.objects.get(email=email)
            send_otp(user, purpose=purpose)
        except ValueError as e:
            return JsonResponse({"success": False, "error": str(e)})

        return JsonResponse({"success": True})
    
    

User = get_user_model()

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email","")

        try:
            email = validate_email_strict(email)
            user = User.objects.get(email=email)
            
            send_otp(user,purpose ="reset")
            
            request.session["otp_purpose"]="reset"
            
            request.session["otp_email"]=email
            
            return redirect("verify_otp")
        except ValidationError as e:
            return render(request,"pages/forgot_password.html",{
                "error":e.message
            })
            
        except User.DoesNotExist:
            return render(request,"pages/forgot_password.html",{
                "error":"Account not found"
            })
        except Exception :
            return render(request,"pages/forgot_password.html",{
                "error":"somehting went wrong.Please try again."
            })

    return render(request, "pages/forgot_password.html")

User = get_user_model()

def reset_password(request):
    if not request.session.get("reset_verified"):
        return redirect("forgot_password")

    email = request.session.get("otp_email")

    if request.method == "POST":
        password = request.POST.get("password","")
        confirm = request.POST.get("confirm_password","")
        
        try:
            password = validate_password_strict(password)
            
            if password != confirm:
                raise ValidationError("Password does not match")
            
        
            

            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()

            request.session.flush()
            messages.success(request, "Password updated successfully")
            return redirect("login")
        
        except ValidationError as e:
            return render(request,"pages/reset_password.html",{
                "error":e.message
            })
            
        except Exception:
            return render(request,"pages/reset_password.html",{
                "error" : "Something went wrong.Plese try again."
            })
        
        

    return render(request, "pages/reset_password.html")



def user_logout(request):
    logout(request)
    return redirect("login")

@user_required
def profile_view(request):
    

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": None},
        {"label": "Profile", "url": None},
    ]

    profile = UserProfile.objects.filter(user=request.user).first()

    return render(request,"account/profile_view.html",{"profile": profile,"breadcrumbs": breadcrumbs,},)

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")



@user_required
def profile_edit(request):
    profile = request.user.profile

   
    if request.user.socialaccount_set.filter(provider="google").exists():
        if request.user.auth_provider != "google":
            request.user.auth_provider = "google"
            request.user.save(update_fields=["auth_provider"])

    if request.method == "POST":

        new_email = request.POST.get("email", "").strip()
        current_email = request.user.email

        if new_email and new_email != current_email:
            if request.user.auth_provider == "google":
                messages.error(
                    request,
                    "Email change is not allowed for Google authenticated accounts"
                )
                return redirect("account_profile_edit")

            try:
                new_email = validate_email_strict(new_email)
            except ValidationError as e:
                messages.error(request, e.message)
                return redirect("account_profile_edit")

            if User.objects.filter(email=new_email).exists():
                messages.error(request, "Email already in use")
                return redirect("account_profile_edit")

            request.session["email_change_new"] = new_email
            request.session["email_change_user"] = request.user.id

            send_otp(
                user=request.user,
                purpose="email_change",
                email_override=new_email
            )

            messages.info(request, "OTP sent to new email")
            return redirect("verify_email_change")

        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        try:
            only_letters_validator(first_name)
            only_letters_validator(last_name)
        except ValidationError:
            messages.error(
                request,
                "First name and last name must contain only alphabets"
            )
            return redirect("account_profile_edit")

     
        phone = request.POST.get("phone", "").strip()

        try:
            phone = validate_phone_number(phone)
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect("account_profile_edit")

        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = phone

        
        image_data = request.POST.get("cropped_image")
        if image_data:
            format, imgstr = image_data.split(";base64,")
            img_bytes = base64.b64decode(imgstr)

            upload_result = cloudinary.uploader.upload(
                img_bytes,
                folder="profile_images",
                public_id=f"user_{request.user.id}",
                overwrite=True,
                invalidate=True,
            )
            profile.profile_image = upload_result["public_id"]


        chest = request.POST.get("chest")
        shoulder = request.POST.get("shoulder")

        try:
            profile.chest = (
                validate_measurement(chest, "chest") if chest else None
            )
            profile.shoulder = (
                validate_measurement(shoulder, "shoulder") if shoulder else None
            )
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("account_profile_edit")

       
        calculated_size = calculate_user_size(
            chest=profile.chest,
            shoulder=profile.shoulder,
        )

        if calculated_size:
            profile.size = calculated_size
        else:
            messages.warning(
                request,
                "We couldn’t determine your size from the given measurements. "
                "Please ensure values are in cm and within a valid range."
            )

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect("account_profile")

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Edit Profile", "url": None},
    ]

    return render(
        request,
        "account/profile_edit.html",
        {"profile": profile, "breadcrumbs": breadcrumbs},
    )


def verify_email_change(request):
    new_email = request.session.get("email_change_new")
    user_id = request.session.get("email_change_user")

    if not new_email or not user_id:
        return redirect("account_profile")

    if request.method == "POST":
        otp_input = request.POST.get("otp", "").strip()

        otp_obj = EmailOTP.objects.filter(
            email=new_email,
            purpose="email_change",
            is_blocked=False
        ).last()

        if not otp_obj or otp_obj.is_expired():
            messages.error(request, "OTP expired or blocked")
            return redirect("verify_email_change")

        if otp_obj.otp != otp_input:
            otp_obj.attempts += 1

            if otp_obj.attempts >= OTP_MAX_ATTEMPTS:
                otp_obj.is_blocked = True
                otp_obj.save()
                messages.error(request, "Too many wrong attempts. OTP blocked.")
                return redirect("account_profile")

            otp_obj.save()
            messages.error(
                request,
                f"Invalid OTP. {OTP_MAX_ATTEMPTS - otp_obj.attempts} attempts left."
            )
            return redirect("verify_email_change")

        user = User.objects.get(id=user_id)
        user.email = new_email
        user.save()

        otp_obj.delete()
        request.session.flush()

        messages.success(request, "Email updated successfully")
        return redirect("account_profile")
    breadcrumbs = [
    {"label": "Home", "url": "/"},
    {"label": "Account", "url": "/account/profile/"},
    {"label": "Change Email", "url": "/account/change-email/"},
    {"label": "Verify Email", "url": None},
]

    return render(request, "account/verify_email_change.html" , {"breadcrumbs": breadcrumbs})

@user_required
def address(request):
   
    
    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by('-is_default','-created_at')
    
    MAX_ADDRESSES=3
    can_add_address = addresses.count() < MAX_ADDRESSES
   
    
    



    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": None},
    ]

    context = {
        'addresses': addresses,  
        'can_add_address': can_add_address,
        'breadcrumbs': breadcrumbs,   
    }

    return render(request,"account/address_list.html",context)



def validate_only_letters(fields_dict):
    for field_name, value in fields_dict.items():

        
        if not value:
            continue

        try:
            only_letters_validator(value)
        except ValidationError:
            raise ValidationError(
                f"{field_name.replace('_', ' ').title()} should contain only alphabets."
            )


def validate_only_numbers(fields_dict):
    for field_name, value in fields_dict.items():

        if not value:
            continue  

        try:
            only_numbers_validator(value)
        except ValidationError:
            raise ValidationError(
                f"{field_name.replace('_', ' ').title()} should contain only numbers."
            )      

@user_required
def address_add(request):
    
    MAX_ADDRESSES = 3
    if UserAddress.objects.filter(user=request.user).count() >= MAX_ADDRESSES:
        messages.error(request, "You can add only up to 3 addresses.")
        return redirect("account_addresses")
  
    
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": "/account/addresses/"},
        {"label": "Add Address", "url": None},
    ]
    
    context = {"breadcrumbs": breadcrumbs}



  
    if request.method == 'POST':
        data ={
            
            "full_name": request.POST.get("full_name", ""),
            "house_name": request.POST.get("house_name", ""),
            "street": request.POST.get("street", ""),
            "landmark": request.POST.get("landmark", ""),
            "city": request.POST.get("city", ""),
            "state": request.POST.get("state", ""),
            "country": request.POST.get("country", ""),
            "phone": request.POST.get("phone", ""),
            "pincode": request.POST.get("pincode", ""),
            "is_default": request.POST.get("is_default") == "on",
        
        }
        context["form"]=data
        
        try:
            full_name=name_with_spaces_max10(data["full_name"],"Name")
            city = alphabets_only_field(data["city"],"City")
            state = alphabets_only_field(data["state"],"State")
           
            country=alphabets_only_field(data["country"],"Country")
            
            street = street_field_validator(data["street"])
            
            phone = numbers_only_field(data["phone"],"Phone number",10)
            pincode = numbers_only_field(data["pincode"],"Pincode",6)
            
        except ValidationError as e:
            messages.error(request,e.message)
            return render(request,"account/address_add.html",context)
        
        if data["is_default"]:
            UserAddress.objects.filter(
                user=request.user,is_default=True).update(is_default=False)
            
        UserAddress.objects.create(
            user=request.user,
            full_name=full_name,
            house_name=data["house_name"].strip(),
            street=street,  
            land_mark=data['landmark'].strip(),
            city=city,
            state=state,
            country=country,
            phone=phone,
            pincode=pincode,
            is_default=data["is_default"],
        )
        
        messages.success(request, "Address added successfully")
        return redirect("account_addresses")  
    return render(request, "account/address_add.html", context)
                 

    




            
@user_required
def address_edit(request, address_uuid):
    address = get_object_or_404(
        UserAddress, uuid=address_uuid, user=request.user
    )

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": "/account/addresses/"},
        {"label": "Edit Address", "url": None},
    ]

    context = {
        "address": address,
        "breadcrumbs": breadcrumbs,
    }

    if request.method == "POST":
        try:
            full_name = request.POST.get("full_name")
            if full_name:
               address.full_name = name_with_spaces_max10(
                request.POST.get("full_name", ""), "Name"
            )

            city = request.POST.get("city")
            if city:
                address.city = alphabets_only_field(city, "City")

            state = request.POST.get("state")
            if state:
                address.state = alphabets_only_field(state, "State")

            country = request.POST.get("country")
            if country:
                address.country = alphabets_only_field(country, "Country")
                
            street = request.POST.get("street", "").strip()
            if not street:
                raise ValidationError("Street is required")
            
            address.street = street_field_validator(street)
            

            phone = request.POST.get("phone")
            if phone:
                address.phone = numbers_only_field(phone, "Phone number", 10)

            pincode = request.POST.get("pincode")
            if pincode:
                address.pincode = numbers_only_field(pincode, "Pincode", 6)

        except ValidationError as e:
            messages.error(
                request,
                e.messages[0] if hasattr(e, "messages") else str(e)
            )
            return render(request, "account/address_edit.html", context)

   
        address.house_name = request.POST.get("house_name", "").strip()
        address.street = request.POST.get("street", "").strip()
        address.land_mark = request.POST.get("land_mark", "").strip()

        is_default = request.POST.get("is_default") == "on"
        if is_default:
            UserAddress.objects.filter(
                user=request.user,
                is_default=True




            ).exclude(id=address.id).update(is_default=False)

        address.is_default = is_default
        address.save()

        messages.success(request, "Address updated successfully")
        return redirect("account_addresses")

    return render(request, "account/address_edit.html", context)

    
@user_required
def address_delete(request, address_uuid):

    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")

    address = get_object_or_404(
        UserAddress,
        uuid=address_uuid,
        user=request.user
    )

    address.delete()
    messages.success(request, "Address deleted successfully")

    return redirect("account_addresses")
    
    
    
    
@user_required
def orders(request):
    if request.user.is_superuser:
        return redirect("login")

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Orders", "url": None},
    ]

    return render(request,"account/orders.html",{"breadcrumbs": breadcrumbs})


@user_required
def change_password(request):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")
        
        try:
            validate_password_strict(new_password)
        except ValidationError as e:
            messages.error(request, e.message)
            return redirect("change_password")


        user = request.user

      
        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect")
            return redirect("change_password")


        if new_password != confirm_password:
            messages.error(request, "New passwords do not match")
            return redirect("change_password")

       
        if old_password == new_password:
            messages.error(request, "New password cannot be same as old password")
            return redirect("change_password")

        user.set_password(new_password)
        user.save()

      
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully")
        return redirect("account_profile")
    
    
    
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Change Password", "url": None},
    ]

    return render(request,"account/password_change.html",{"breadcrumbs": breadcrumbs})

@user_required
def toggle_user_size_filter(request):
  

    current = request.session.get("ignore_user_size", False)

  
    request.session["ignore_user_size"] = not current
    request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER", "/"))


@user_required
def user_coupons(request):
    user = request.user

    used_coupon_ids = CouponUsage.objects.filter(
        user=user
    ).values_list("coupon_id", flat=True)

    coupons = Coupon.objects.filter(
        is_active=True
    ).order_by("-created_at")

    coupon_list = []

    for coupon in coupons:
        coupon_list.append({
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "min_purchase_amount": coupon.min_purchase_amount,
            "valid_to": coupon.valid_to,
            "is_used": coupon.id in used_coupon_ids,
        })
        
    paginator = Paginator(coupon_list, 5)

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Profile", "url": None},
        {"label": "My Coupons", "url": None},
    ]

    context = {
        "breadcrumbs": breadcrumbs,
        "coupons": coupon_list,
          "page_obj": page_obj,
        "today": now().date(),
    }

    return render(request, "account/profile_coupons.html", context)