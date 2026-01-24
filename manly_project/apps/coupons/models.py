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

    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Applicable only for percentage coupons"
    )

    is_active = models.BooleanField(default=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):

        if self.discount_type == "PERCENT":
            if self.discount_value > 90:
                raise ValidationError("Percentage discount cannot exceed 90%")

            if not self.max_discount_amount:
                raise ValidationError("Max discount amount is required for percentage coupons")

        start = self.start_date
        end = self.end_date

        if timezone.is_naive(start):
            start = timezone.make_aware(start)

        if timezone.is_naive(end):
            end = timezone.make_aware(end)

        if end < start:
            raise ValidationError("End date cannot be earlier than start date")

        if end < timezone.now():
            raise ValidationError("End date cannot be in the past")

    def __str__(self):
        return self.code


class CouponUsage(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="used_coupons"
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="usages"
    )

    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "coupon")

    def __str__(self):
        return f"{self.user} used {self.coupon.code}"
