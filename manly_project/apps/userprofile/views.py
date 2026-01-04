from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import UserProfile ,UserAddress
from apps.sizeguide.models import SizeGuide


@login_required
def profile_view(request):
    if request.user.is_superuser:
        return redirect("login")

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": None},
        {"name": "Profile", "url": None},
    ]

    profile = UserProfile.objects.filter(user=request.user).first()

    return render(
        request,
        "account/profile_view.html",
        {
            "profile": profile,
            "breadcrumbs": breadcrumbs,
        },
    )



@login_required
def profile_edit(request):
    if request.user.is_superuser:
        return redirect("login")

    profile = UserProfile.objects.filter(user=request.user).first()

    if not profile:
        messages.error(request, "Profile not found")
        return redirect("account_profile")

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Edit Profile", "url": None},
    ]

    if request.method == "POST":
        profile.first_name = request.POST.get("first_name", "").strip()
        profile.last_name = request.POST.get("last_name", "").strip()
        profile.phone = request.POST.get("phone", "").strip()

        chest = request.POST.get("chest")
        shoulder = request.POST.get("shoulder")

        profile.chest = float(chest) if chest else None
        profile.shoulder = float(shoulder) if shoulder else None

        profile.size = ""

        if profile.chest:
            size_match = SizeGuide.objects.filter(
                is_active=True,
                chest_min__lte=profile.chest,
                chest_max__gte=profile.chest,
            ).first()

            if size_match:
                profile.size = size_match.size_name

        profile.save()
        messages.success(request, "Profile updated successfully")
        return redirect("account_profile")

    return render(
        request,
        "account/profile_edit.html",
        {
            "profile": profile,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def address(request):
    if request.user.is_superuser:
        return redirect('login')
    
    addresses = UserAddress.objects.filter(
        user=request.user
    ).order_by('-is_default','-created_at')



    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Address", "url": None},
    ]
    context = {
        'addresses' : addresses,
        'breadcrumps' : breadcrumbs,
    }

    return render(request,"account/address_list.html",context)

@login_required
def address_add(request):
    if request.user.is_superuser:
        return redirect('login')

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Address", "url": "/account/addresses/"},
        {"name": "Add Address", "url": None},
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
            return render(
                request,
                'account/address_add.html',
                {"breadcrumbs": breadcrumbs}
            )

       
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

    return render(
        request,
        'account/address_add.html',
        {'breadcrumbs': breadcrumbs}
    )

@login_required
def address_edit(request,address_id):
    if request.user.is_superuser:
        return redirect('login')
    
    address = get_object_or_404(
        UserAddress,id=address_id,user=request.user
    )
    
    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Address", "url": "/account/addresses/"},
        {"name": "Edit Address", "url": None},
    ]
    
    is_default = request.POST.get('is_default') == 'on'
    
    if is_default :
        UserAddress.objects.filter(
            user = request.user,is_default=True
        ).exclude(id=address.id).update(is_default=False) 
        
        
        address.is_default = is_default 
        address.save()
        
        
        messages.success(request,'Address updated successfully')
        return redirect('account_addresses')
    
    
    return render(request,'account/address_edit.html',{'address': address})  
    
    
@login_required
def address_delete(request, address_id):

    if request.user.is_superuser:
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
    if not request.user.is_authenticated or request.user.is_superuser:
        return redirect('login')

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Orders", "url": None},
    ]

    return render(request,"account/orders.html",{"breadcrumbs": breadcrumbs})


@login_required
def password_change(request):
    if not request.user.is_authenticated or request.user.is_superuser:
        return redirect('login')

    breadcrumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Account", "url": "/account/profile/"},
        {"name": "Change Password", "url": None},
    ]

    return render(request,"account/password.html",{"breadcrumbs": breadcrumbs})


@login_required
def account_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect("login")
