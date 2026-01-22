from django.contrib.auth import update_session_auth_hash

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from apps.accounts.models import EmailOTP

from apps.accounts.models import UserProfile, UserAddress
from apps.sizeguide.models import SizeGuide
from .utils import send_otp
from .validators import only_letters_validator, only_numbers_validator
from django.core.exceptions import ValidationError
from apps.accounts.services.size_mapping import calculate_user_size

import cloudinary.uploader
import base64



User = get_user_model()


def user_login(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_active:
                error = "Please verify your account"
            else:
                login(request, user)
                return redirect("home")
        else:
            error = "Invalid email or password"

    return render(request, "pages/login.html", {"error": error})


def user_signup(request):
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            error = "Passwords do not match"
        else:
            existing_user = User.objects.filter(email=email).first()

            try:
                if existing_user:
                    if not existing_user.is_active:
                        send_otp(existing_user, purpose="signup")
                        request.session["otp_user"] = existing_user.id
                    else:
                        error = "Email already registered"
                        return render(request, "pages/signup.html", {"error": error})
                else:
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        is_active=False
                    )
                    send_otp(user, purpose="signup")
                    request.session["otp_user"] = user.id

                request.session["otp_purpose"] = "signup"
                request.session["otp_email"] = email
                return redirect("verify_otp")

            except ValueError as e:
                messages.error(request, str(e))
                return redirect("signup")

    return render(request, "pages/signup.html", {"error": error})



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
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, "pages/forgot_password.html", {
                "error": "Account not found"
            })

        send_otp(user, purpose="reset")

        request.session["otp_purpose"] = "reset"
        request.session["otp_email"] = email

        return redirect("verify_otp")

    return render(request, "pages/forgot_password.html")

User = get_user_model()

def reset_password(request):
    if not request.session.get("reset_verified"):
        return redirect("forgot_password")

    email = request.session.get("otp_email")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            return render(request, "pages/reset_password.html", {
                "error": "Passwords do not match"
            })

        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()

        request.session.flush()
        messages.success(request, "Password updated successfully")
        return redirect("login")

    return render(request, "pages/reset_password.html")



def user_logout(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")

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



@login_required
def profile_edit(request):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    profile = request.user.profile

    if request.user.socialaccount_set.filter(provider="google").exists():
        if request.user.auth_provider != "google":
            request.user.auth_provider = "google"
            request.user.save(update_fields=["auth_provider"])

    if request.method == "POST":
        new_email = request.POST.get("email", "").strip()
        current_email = request.user.email
        if request.user.auth_provider == "google" and new_email != current_email:
            messages.error(
                request,
                "Email change is not allowed for Google authenticated accounts"
            )
            return redirect("account_profile_edit")

        if new_email and new_email != current_email:

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
                "First name and Last name should contain only alphabets."
            )
            return redirect("account_profile_edit")

        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = request.POST.get("phone", "").strip()

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

        profile.chest = float(chest) if chest else None
        profile.shoulder = float(shoulder) if shoulder else None

        profile.size = calculate_user_size(
            chest=profile.chest,
            shoulder=profile.shoulder,
        )

        profile.save()
        messages.success(request, "Profile updated successfully")
    
    
        return redirect("account_profile")
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Edit Profile", "url": None},
        ]
       

    return render(request, "account/profile_edit.html",  {"profile": profile,"breadcrumbs": breadcrumbs,})





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

    
@login_required
def address(request):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by('-is_default','-created_at')



    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": None},
    ]

    context = {
        'addresses': addresses,  
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

@login_required
def address_add(request):
    
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": "/account/addresses/"},
        {"label": "Add Address", "url": None},
    ]


  
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        house_name = request.POST.get('house_name', '').strip()
        street = request.POST.get('street', '').strip()
        landmark = request.POST.get('landmark', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        country = request.POST.get('country', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        
        
        

        
        if not all([full_name, phone, house_name, street, city, state, country, pincode]):
            messages.error(request, 'Please fill all required fields')
            return render(request, 'account/address_add.html', {"breadcrumbs": breadcrumbs})

      
        try:
            validate_only_letters({
                "full_name": full_name,
                "street": street,
                "landmark": landmark,
                "city": city,
                "state": state,
                "country": country,
            })
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'account/address_add.html', {"breadcrumbs": breadcrumbs})
        
        try:
            validate_only_numbers({
                "phone": phone,
                "pincode": pincode,
            })
        except ValidationError as e:
            messages.error(request, str(e))
            return render(request, 'account/address_add.html', {"breadcrumbs": breadcrumbs})
        if len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return render(request, 'account/address_add.html', {"breadcrumbs": breadcrumbs})

        if len(pincode) != 6:
            messages.error(request, "Pincode must be exactly 6 digits.")
            return render(request, 'account/address_add.html', {"breadcrumbs": breadcrumbs})

       
        if is_default:
            UserAddress.objects.filter(
                user=request.user,
                is_default=True
            ).update(is_default=False)

        UserAddress.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            house_name=house_name,
            street=street,
            land_mark=landmark,
            city=city,
            state=state,
            country=country,
            pincode=pincode,
            is_default=is_default,
        )

        messages.success(request, 'Address added successfully')
        return redirect('account_addresses')
            
        

    return render(request,'account/address_add.html',{'breadcrumbs': breadcrumbs})




            
@login_required
def address_edit(request,address_id):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    address = get_object_or_404(
        UserAddress,id=address_id,user=request.user
    )
    

     
    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        street = request.POST.get("street", "").strip()
        landmark = request.POST.get("landmark", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        country = request.POST.get("country", "").strip()
        phone = request.POST.get("phone", "").strip()
        pincode = request.POST.get("pincode", "").strip()

   
        try:
            validate_only_letters({
                "full_name": full_name,
                "street": street,
                "landmark": landmark,
                "city": city,
                "state": state,
                "country": country,
            })
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("account_address_edit", address_id=address.id)
        
        
        try:
            validate_only_numbers({
                 "phone": phone,
                    "pincode": pincode,
            })
        except ValidationError as e:
            messages.error(request, str(e))
            return redirect("account_address_edit", address_id=address.id)
        
        
        if len(phone) != 10:
            messages.error(request, "Phone number must be exactly 10 digits.")
            return redirect("account_address_edit", address_id=address.id)

        if len(pincode) != 6:
            messages.error(request, "Pincode must be exactly 6 digits.")
            return redirect("account_address_edit", address_id=address.id)

        address.full_name = full_name
        address.street = street
        address.land_mark = landmark
        address.city = city
        address.phone=phone
        address.state = state
        address.country = country
        address.pincode = pincode
    
        is_default = request.POST.get('is_default') == 'on'
        
        
        if is_default :
            UserAddress.objects.filter(
                user = request.user,is_default=True
            ).exclude(id=address.id).update(is_default=False) 
            
            
        address.is_default = is_default 
        address.save()
        
        
        messages.success(request,'Address updated successfully')
        return redirect('account_addresses')

    
    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Address", "url": "/account/addresses/"},
        {"label": "Edit Address", "url": None},
    ]
    context = {
        'address': address,
        'breadcrumbs': breadcrumbs,
    }
    
    
    return render(request,'account/address_edit.html',context)  
    
    
@login_required
def address_delete(request, address_id):

    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")

    address = get_object_or_404(
        UserAddress,
        id=address_id,
        user=request.user
    )

    address.delete()
    messages.success(request, "Address deleted successfully")

    return redirect("account_addresses")
    
    
    
    
@login_required
def orders(request):
    if request.user.is_superuser:
        return redirect("login")

    breadcrumbs = [
        {"label": "Home", "url": "/"},
        {"label": "Account", "url": "/account/profile/"},
        {"label": "Orders", "url": None},
    ]

    return render(request,"account/orders.html",{"breadcrumbs": breadcrumbs})


@login_required
def change_password(request):
    if request.user.is_superuser  or not request.user.is_authenticated:
        return redirect("login")
    
    
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

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


@login_required
def toggle_user_size_filter(request):
    """
    Toggle user-size-based product prioritization.
    Stored in session only.
    """

    current = request.session.get("ignore_user_size", False)

  
    request.session["ignore_user_size"] = not current
    request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER", "/"))