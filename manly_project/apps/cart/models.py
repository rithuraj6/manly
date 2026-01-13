from django.conf import settings
from django.db import models
from apps.products.models import Product, ProductVariant




User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='cart')
    
    is_active =models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Cart ({self.user})'
    
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant,on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default =1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta :
        
        unique_together = ('cart','product','variant')
        
    def __str__ (self):
        
        return f'{self.product.name} ({self.variant.name} x {self.quantity})'
  

