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
        min_purchase = self.min_purchase_amount or Decimal("0")
        discount_value = self.discount_value or Decimal("0")
        max_discount = self.max_discount_amount or Decimal("0")

        
        if self.valid_from and self.valid_to:
            if self.valid_to < self.valid_from:
                raise ValidationError("Valid To date cannot be earlier than Valid From date")
            if self.valid_to < timezone.now().date():
                raise ValidationError("Valid To date cannot be in the past")

        
        if min_purchase <= 0:
            raise ValidationError("Minimum purchase amount must be greater than zero")

        max_allowed_by_rule = min_purchase * Decimal("0.25")

       
        if self.discount_type == "FLAT":
            if max_discount <= 0:
                raise ValidationError("Max discount amount is required for flat coupons")

            if max_discount > max_allowed_by_rule:
                raise ValidationError(
                    "Max discount amount cannot exceed 25% of minimum purchase amount"
                )

      
            self.discount_value = Decimal("0.00")

       
        if self.discount_type == "PERCENT":
            if discount_value <= 0 or discount_value > 90:
                raise ValidationError("Percentage discount must be between 1 and 90")

            if max_discount <= 0:
                raise ValidationError("Max discount amount is required for percentage coupons")

        
            if max_discount > max_allowed_by_rule:
                raise ValidationError(
                    "Max discount amount cannot exceed 25% of minimum purchase amount"
                )

          
            max_possible_percent_discount = (
                min_purchase * discount_value / Decimal("100")
            )

            if max_discount > max_possible_percent_discount:
                raise ValidationError(
                    "Max discount amount cannot exceed calculated percentage discount"
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
