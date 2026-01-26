from django.db import models

from django.conf import settings
from apps.products.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="wishlist")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"wishlist({self.user})"
    
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE,related_name="items")
    
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("wishlist","product")
        
    def __str__(self):
        return f"{self.product.name} in wishlist"


    