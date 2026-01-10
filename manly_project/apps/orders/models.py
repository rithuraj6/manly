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
        ("partially_cancelled", "Partially Cancelled"),
        ("partially_returned", "Partially Returned"),
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

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
    STATUS_RETURN_REQUESTED = "return_requested"
    STATUS_RETURNED = "returned"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_SHIPPED, "Shipped"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_RETURN_REQUESTED, "Return Requested"),
        (STATUS_RETURNED, "Returned"),
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

    
    final_price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final amount paid for this item (used for refunds)"
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True 
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






class ReturnRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    REASON_WRONG_SIZE = "wrong_size"
    REASON_DAMAGED = "damaged"
    REASON_QUALITY = "quality"
    REASON_WRONG_ITEM = "wrong_item"
    REASON_LATE_DELIVERY = "late_delivery"
    REASON_CHANGED_MIND = "changed_mind"
    REASON_OTHER = "other"

    REASON_CHOICES = [
        (REASON_WRONG_SIZE, "Wrong size"),
        (REASON_DAMAGED, "Damaged product"),
        (REASON_QUALITY, "Quality not as expected"),
        (REASON_WRONG_ITEM, "Wrong item delivered"),
        (REASON_LATE_DELIVERY, "Late delivery"),
        (REASON_CHANGED_MIND, "Changed mind"),
        (REASON_OTHER, "Other"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="return_requests"
    )

    order_item = models.OneToOneField(
        "OrderItem",
        on_delete=models.CASCADE,
        related_name="return_request"
    )

    reason = models.CharField(
        max_length=30,
        choices=REASON_CHOICES
    )

    description = models.TextField(
        blank=True,
        help_text="Required only if reason is 'Other'"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ReturnRequest #{self.id} - OrderItem {self.order_item.id}"


