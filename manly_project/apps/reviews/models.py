from django.db import models
from django.conf import settings
from apps.products.models import Product
from apps.orders.models import OrderItem


class ProductReview(models.Model):

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="review"
    )
   

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    review_text = models.TextField()

    is_approved = models.BooleanField(default=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    

    def __str__(self):
        return f"{self.product.name} - {self.rating}★"
