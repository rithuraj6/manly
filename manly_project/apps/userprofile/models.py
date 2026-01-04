from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    chest = models.FloatField(null=True, blank=True)
    shoulder = models.FloatField(null=True, blank=True)

    size = models.CharField(max_length=5, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
            return self.user.email


class UserAddress(models.Model):
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='addresses')
    
    
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    house_name = models.CharField(max_length=220)
    street = models.CharField(max_length=225)
    city = models.CharField(max_length=225)
    Land_mark = models.CharField(max_length = 225, blank= True)
    state = models.CharField(max_length=225)
    
    country = models.CharField(max_length = 100)
    pincode  = models.CharField(max_length=10)
    
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta :
        ordering = ["-is_default", "-created_at"]

        
    def __str__ (self):
        return f"{self.full_name} - {self.city}"

    