from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid
from decimal import Decimal

class Coupon(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    DISCOUNT_TYPE_CHOICES = (
        ("FLAT", "Flat Amount"),
        ("PERCENT", "Percentage"),
    )

    code = models.CharField(max_length=50, unique=True)

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        db_column="min_purchase_amount"
    )

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="max_discount_amount"
    )

    is_active = models.BooleanField(default=True)

    valid_from = models.DateField(db_column="valid_from")
    valid_to = models.DateField(db_column="valid_to")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


    def clean(self):
        
      
        if self.discount_type == "PERCENT":
            if self.discount_value > 90:
                raise ValidationError("Percentage discount cannot exceed 90%")

            if not self.max_discount_amount:
                raise ValidationError(
                    "Max discount amount is required for percentage coupons"
                )

        if self.valid_from and self.valid_to:
            if self.valid_to < self.valid_from:
                raise ValidationError(
                    "Valid To date cannot be earlier than Valid From date"
                )

            if self.valid_to < timezone.now().date():
                raise ValidationError(
                    "Valid To date cannot be in the past"
                )
        min_purchase = self.min_purchase_amount or Decimal("0")
        discount_value = self.discount_value or Decimal("0")
        max_discount = self.max_discount_amount  or Decimal("0")
        
        if self.discount_type =="FLAT":
            if min_purchase <=0:
                raise ValidationError("Minimum purchase amount is required for flat coupons")
            
            
            if discount_value > min_purchase:
                raise ValidationError("Flat discount cannot be greater than minimum purchase amount")
            
            
        if self.discount_type == "PERCENT":
            
            if  min_purchase > 0 and max_discount > min_purchase:
                raise ValidationError(
                    "Max dicount amount exceed minimum purchase amount"
                )


    def __str__(self):
        return self.code


class CouponUsage(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="used_coupons"
    )

    coupon = models.ForeignKey(
        "coupons.Coupon",
        on_delete=models.CASCADE,
        related_name="usages"
    )

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coupon")

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"
