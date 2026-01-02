"""
URL configuration for manly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.userprofile.models import UserProfile



urlpatterns = [

    path("accounts/", include("apps.accounts.urls")),

  
    path("accounts/", include("allauth.urls")),

    
    path("", include("apps.core.urls")),

  
    path("account/", include("apps.userprofile.urls")),

   
    path("", include("apps.products.urls")),
    path("cart/", include("apps.cart.urls")),
    path("wishlist/", include("apps.wishlist.urls")),

    path("admin/", admin.site.urls),
    path("admin-panel/", include("apps.adminpanel.urls")),
    
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

