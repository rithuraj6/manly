from django.db import models
from apps.categories.models import Category

class Product(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        Category,on_delete=models.PROTECT,
        related_name = "products"
    )
    
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)  # soft delete

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    

# Create your models here.
