from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Coupon(models.Model):

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
        
        # Percentage validation
        if self.discount_type == "PERCENT":
            if self.discount_value > 90:
                raise ValidationError("Percentage discount cannot exceed 90%")

            if not self.max_discount_amount:
                raise ValidationError(
                    "Max discount amount is required for percentage coupons"
                )

        # Date validation (ONLY valid_from / valid_to)
        if self.valid_from and self.valid_to:
            if self.valid_to < self.valid_from:
                raise ValidationError(
                    "Valid To date cannot be earlier than Valid From date"
                )

            if self.valid_to < timezone.now().date():
                raise ValidationError(
                    "Valid To date cannot be in the past"
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
