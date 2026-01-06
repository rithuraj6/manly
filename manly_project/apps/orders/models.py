from django.db import models
from django.conf import settings
from django.utils import timezone

from apps.products.models import Product, ProductVariant



class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out for Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("cod", "Cash on Delivery"),
       
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_id = models.CharField(
        max_length=30,
        unique=True,
        db_index=True
    )

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default="pending"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="cod"
    )

    is_paid = models.BooleanField(default=False)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    address_snapshot = models.JSONField()


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order_id



class OrderItem(models.Model):

    ITEM_STATUS_CHOICES = [
        ("active", "Active"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=ITEM_STATUS_CHOICES,
        default="active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(max_length=30)
    changed_by = models.CharField(max_length=30, default="admin")
    changed_at = models.DateTimeField(auto_now_add=True)



class OrderAction(models.Model):

    ACTION_TYPE_CHOICES = [
        ("cancel", "Cancel"),
        ("return", "Return"),
    ]

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="actions"
    )

    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPE_CHOICES
    )

    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

