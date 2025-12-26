from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,PermissionsMixin,BaseUserManager

    )

from django.utils import timezone



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




class User(AbstractBaseUser ,PermissionsMixin):
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
        

from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    PURPOSE_CHOICES = (
        ("signup", "Signup"),
        ("reset", "Password Reset"),
    )

    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.email} - {self.purpose}"


import uuid
from datetime import timedelta
from django.utils import timezone

class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete = models.CASCADE,
        related_name = "password_reset_token"
        
    )     
    
    token = models.UUIDField(default = uuid.uuid4, unique =True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    