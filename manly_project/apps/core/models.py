from django.db import models
from cloudinary.models import CloudinaryField

class SiteBanner(models.Model):
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=150, blank=True)
    image = CloudinaryField("banner_image")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
