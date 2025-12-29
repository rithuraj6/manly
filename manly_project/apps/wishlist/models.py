from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Wishlist(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )
    products = models.ManyToManyField(
        "products.Product",
        blank=True
    )

    def __str__(self):
        return f"{self.user} wishlist"
