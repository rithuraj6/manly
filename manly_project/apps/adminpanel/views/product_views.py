from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from apps.accounts.decorators import admin_required

from apps.products.models import Product, ProductVariant, ProductImage
from apps.categories.models import Category
from apps.products.validators import validate_product_price
from django.core.exceptions import ValidationError


@admin_required
def admin_product_list(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")
    
    search = request.GET.get("search", "").strip()

    products = Product.objects.select_related("category")

    if search:
        products = products.filter(name__icontains=search)

    products = products.order_by("-created_at")

    paginator = Paginator(products, 7)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "adminpanel/products/product_list.html",
        {
            "page_obj": page_obj,
            "search": search,
        },
    )




@admin_required
def admin_add_product(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    categories = Category.objects.all()

    if request.method == "POST":
        is_featured = request.POST.get("is_featured") == "on"
        
        try:
            price = validate_product_price(request.POST.get('price'))
            
        except ValidationError as e:
            
            return render(request,'adminpanel/product/product_edit.html',{'categories':categories})
        

        product = Product.objects.create(
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            base_price=price,
            category_id=request.POST.get("category"),
            is_active=True,
            is_featured=is_featured,  
    )


        messages.success(request, "Product created. Add images and variants.")
        return redirect("admin_edit_product", product_uuid=product.uuid)

    return render(
        request,
        "adminpanel/products/product_edit.html",
        {"categories": categories},
    )





@admin_required
def admin_edit_product(request, product_uuid):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    product = get_object_or_404(Product, uuid=product_uuid)
    variants = product.variants.all().order_by("size")
    categories = Category.objects.all()
    images = product.images.all()

    if request.method == "POST":
        product.is_featured = request.POST.get("is_featured") == "on"
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
       
        product.category_id = request.POST.get("category")
        
        
        try:
            product.base_price = validate_product_price(
                request.POST.get('price')
                
                
            )
        except ValidationError as e:
            messages.error(request,str(e))
            return render(request,'adminpanel/products/product_edit.html',{"product":product,"variants":variants,"categories":categories,"images":images,},)
        product.save()

        messages.success(request, "Product updated successfully")

       
        return redirect("admin_product_list")

    return render(
        request,
        "adminpanel/products/product_edit.html",
        {
            "product": product,
            "variants": variants,
            "categories": categories,
            "images": images,
        },
    )

@admin_required
def admin_upload_product_image(request, product_uuid):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")


    if request.method == "POST" and request.FILES.get("image"):
        product = get_object_or_404(Product, uuid=product_uuid)

        image = ProductImage.objects.create(
            product=product,
            image=request.FILES["image"]
        )

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@admin_required
def admin_delete_product_image(request, image_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    if request.method == "POST":
        image = get_object_or_404(ProductImage, id=image_id)

      
        if hasattr(image.image, "delete"):
            image.image.delete(save=False)

        image.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)

@admin_required
def admin_add_variant(request, product_uuid):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    product = get_object_or_404(Product,uuid=product_uuid)

    if request.method == "POST":
        size = request.POST.get("size")
        stock = request.POST.get("stock")

        
        allowed_sizes = dict(ProductVariant.SIZE_CHOICES)
        if size not in allowed_sizes:
            messages.error(request, "Invalid size selected.")
            return redirect("admin_edit_product", product_id=product.id)

        if ProductVariant.objects.filter(product=product, size=size).exists():
            messages.error(request, f"Variant {size} already exists.")
            return redirect("admin_edit_product", product_id=product.id)

        ProductVariant.objects.create(
            product=product,
            size=size,
            stock=stock,
            is_active=True,
        )

        messages.success(request, f"Variant {size} added successfully.")

    
    return redirect("admin_edit_product", product_uuid=product.uuid)



@admin_required
def admin_update_variant(request, variant_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    variant = get_object_or_404(ProductVariant, id=variant_id)

    if request.method == "POST":
        variant.stock = request.POST.get("stock")
        variant.save()
        messages.success(request, "Variant stock updated")

    return redirect("admin_edit_product", product_uuid=variant.product.uuid)


@admin_required
def admin_toggle_variant(request, variant_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    variant = get_object_or_404(ProductVariant, id=variant_id)
    variant.is_active = not variant.is_active
    variant.save()

    messages.success(request, "Variant status updated")
    return redirect("admin_edit_product", product_uuid=variant.product.uuid)



@admin_required
def admin_toggle_product(request, product_uuid):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect("admin_login")

    product = get_object_or_404(Product, uuid=product_uuid)
    product.is_active = not product.is_active
    product.save()

    messages.success(request, "Product status updated")
    return redirect("admin_product_list")

