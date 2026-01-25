from django.urls import path

from .views.auth_views import admin_login, admin_logout
from .views.dashboard_views import admin_dashboard
from .views.user_views import admin_users, toggle_user_status
from .views.category_views import (
    admin_category_list,
    admin_add_category,
    admin_edit_category,
    admin_toggle_category_status,
    
)
from .views.product_views import (
    admin_product_list,
    admin_edit_product,
    admin_add_variant,
    admin_toggle_variant,
    admin_add_product,
    admin_update_variant,
    admin_toggle_product,
    admin_delete_product_image,
    admin_upload_product_image,
)


from .views.banner_views import (
    admin_banner_list,
    admin_add_banner,
    admin_toggle_banner,
    
)

from apps.adminpanel.views.return_views import (
    admin_return_request_list,
    admin_reject_return,
)


from apps.adminpanel.views.order_views import (
    admin_order_list,
    admin_order_edit,
    admin_order_update,
    admin_order_update_success,
)




from apps.adminpanel.views.inventory_views import (
    inventory_category_list,
    inventory_product_list,
)

from apps.adminpanel.views.wallet_views import admin_wallet_dashboard


from apps.adminpanel.views.return_views import approve_return

from apps.adminpanel.views.offers_views import (
    offer_list,
    offer_add,
    offer_edit,
    toggle_offer_status,
)
from .views.coupon_views import coupon_list, toggle_coupon_status ,add_coupon,edit_coupon



urlpatterns = [
    path("login/", admin_login, name="admin_login"),
    path("logout/", admin_logout, name="admin_logout"),

    path("dashboard/", admin_dashboard, name="admin_dashboard"),

    path("users/", admin_users, name="admin_users"),
    path("users/toggle/<int:user_id>/", toggle_user_status, name="toggle_user"),

    
    path("categories/", admin_category_list, name="admin_category_list"),
    path("categories/add/", admin_add_category, name="admin_add_category"),
    path("categories/edit/<int:category_id>/", admin_edit_category, name="admin_edit_category"),
    path("categories/toggle/<int:category_id>/", admin_toggle_category_status, name="admin_toggle_category"),
    
    
    path("products/", admin_product_list, name="admin_product_list"),
    path("products/edit/<int:product_id>/", admin_edit_product, name="admin_edit_product"),
    path("products/<int:product_id>/variants/add/", admin_add_variant, name="admin_add_variant"),
    path("variants/toggle/<int:variant_id>/", admin_toggle_variant, name="admin_toggle_variant"),
    path("products/add/", admin_add_product, name="admin_add_product"),
    path("variants/update/<int:variant_id>/", admin_update_variant, name="admin_update_variant"),
    path("products/toggle/<int:product_id>/", admin_toggle_product, name="admin_toggle_product"),
    path("products/<int:product_id>/images/upload/",admin_upload_product_image,name="admin_upload_product_image"),
    
    
    
    
    path("orders/", admin_order_list, name="admin_order_list"),
    path("orders/update-success/",admin_order_update_success,name="admin_order_update_success"),
    path("orders/<str:order_id>/", admin_order_edit, name="admin_order_edit"),
    path("orders/<str:order_id>/update/", admin_order_update, name="admin_order_update"),

    
    path("wallet/", admin_wallet_dashboard, name="admin_wallet"),

    
    
    
    

    path("products/images/delete/<int:image_id>/",admin_delete_product_image,name="admin_delete_product_image"),

    path("banners/", admin_banner_list, name="admin_banner_list"),
  
    path("banners/add/", admin_add_banner, name="admin_add_banner"),
    path("banners/toggle/<int:banner_id>/", admin_toggle_banner, name="admin_toggle_banner"),
    path("returns/", admin_return_request_list, name="admin_return_request_list"),
    path("returns/approve/<int:return_id>/", approve_return, name="admin_approve_return"),
    path("returns/reject/<int:return_id>/", admin_reject_return, name="admin_reject_return"),
    
    
    path("offers/", offer_list, name="admin_offer_list"),
    path("offers/add/", offer_add, name="admin_offer_add"),
    path("offers/<int:offer_id>/toggle/",toggle_offer_status,name="admin_offer_toggle"),
    path("offers/<int:offer_id>/edit/",offer_edit,name="admin_offer_edit"),
    
    
    
    
    path("coupons/", coupon_list, name="admin_coupon_list"),
    path("coupons/<int:coupon_id>/toggle/", toggle_coupon_status, name="admin_coupon_toggle"),
    path("coupons/add/", add_coupon, name="admin_coupon_add"),
    path("coupons/<int:coupon_id>/edit/",edit_coupon,name="admin_coupon_edit"),




    
    
    path("inventory/", inventory_category_list, name="inventory_categories"),
    path("inventory/<int:category_id>/",inventory_product_list,name="inventory_products"),


]
