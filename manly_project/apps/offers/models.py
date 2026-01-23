from django.db import models
from apps.categories.models import Category
from apps.products.models import Product
from django.utils import timezone
from django.core.exceptions import ValidationError




class Offer(models.Model):
    name = models.CharField(max_length=100)
    
    discount_percentage = models.PositiveIntegerField(
        help_text="Enter a Percentage value between 10 and 90 "
    )
    
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True,blank=True,related_name="offers")
    
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True,blank=True,related_name='offers')
    
    is_active =models.BooleanField(default=True)
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.product and self.category:
            raise ValidationError("Select either product or category, not both.")

        if not self.product and not self.category:
            raise ValidationError("You must select a product or a category.")
        
        if self.discount_percentage > 90:
            raise ValidationError('Discount percentage  cannnot exceed 90')
   
            
        if self.start_date and self.end_date:
            start = self.start_date
            end = self.end_date

            if timezone.is_naive(start):
                start = timezone.make_aware(start)

            if timezone.is_naive(end):
                end = timezone.make_aware(end)

            if end < start:
                raise ValidationError("End date cannot be earlier than start date.")

            if end < timezone.now():
                raise ValidationError("End date cannot be in the past.")