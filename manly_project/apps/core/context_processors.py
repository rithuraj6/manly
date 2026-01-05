from django.conf import settings

def cloudinary_settings(request):
    return {
        "CLOUDINARY_CLOUD_NAME": settings.CLOUDINARY_CLOUD_NAME
    }
