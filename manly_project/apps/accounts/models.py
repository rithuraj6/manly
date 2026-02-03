from django.db import models
from django.utils import timezone
from datetime import timedelta
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,PermissionsMixin,BaseUserManager

    )
import uuid



class UserManager(BaseUserManager):


    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError("The Email Field must not be empty")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True

        return self.create_user(email, password, **extra_fields)


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    
    profile_image = CloudinaryField(
        "profile_image",
        blank=True,
        null=True
    )


    chest = models.FloatField(null=True, blank=True)
    shoulder = models.FloatField(null=True, blank=True)
    size = models.CharField(max_length=5, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

User = settings.AUTH_USER_MODEL



class UserAddress(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='addresses')
    
    
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
    house_name = models.CharField(max_length=220)
    street = models.CharField(max_length=225)
    city = models.CharField(max_length=225)
    land_mark = models.CharField(max_length = 225, blank= True)
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

    
class User(AbstractBaseUser ,PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,  unique=True)
    
    
    
    AUTH_PROVIDERS = (
        ("email", "Email"),
        ("google", "Google"),
    )

    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_PROVIDERS,
        default="email"
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default =False)
    is_blocked =  models.BooleanField(default=False)

    created_at = models.DateField(default=timezone.now)
    updated_at = models.DateField(auto_now=True)

    objects = UserManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    def __str__ (self):
        return self.email
        

class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ("signup", "Signup"),
        ("reset", "Password Reset"),
        ("email_change", "Email Change"),
    )

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=12, choices=PURPOSE_CHOICES)
    
    
    attempts = models.PositiveSmallIntegerField(default=0)  
    is_blocked = models.BooleanField(default=False)          

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=["email", "created_at"]),
        ]
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    
    
class SecurityAuditLog(models.Model):
    ACTION_CHOICES = (
        ("otp_sent", "OTP Sent"),
        ("otp_failed", "OTP Failed"),
        ("otp_blocked", "OTP Blocked"),
        ("email_changed", "Email Changed"),
        ("password_reset", "Password Reset"),
        ("signup_verified", "Signup Verified"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email = models.EmailField()
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.action}"
