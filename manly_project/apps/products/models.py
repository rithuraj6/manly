from django.db import models
from apps.categories.models import Category
from PIL import Image
from django.db import models

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
    
cclass ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        # Convert to RGB (fix PNG / CMYK issues)
        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        min_side = min(width, height)

        # Center crop
        left = (width - min_side) / 2
        top = (height - min_side) / 2
        right = (width + min_side) / 2
        bottom = (height + min_side) / 2

        img = img.crop((left, top, right, bottom))

        # Resize
        img = img.resize((800, 800), Image.LANCZOS)

        # Save optimized
        img.save(
            self.image.path,
            quality=85,
            optimize=True
        )

