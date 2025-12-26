from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100 , unique = True)
    is_active = models.BooleanField(default =True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.name
    