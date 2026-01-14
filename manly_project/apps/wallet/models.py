from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL

class Wallet(models.Model):
    
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='wallet')
    balance = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} - ₹{self.balance}"
    
    
    
    
    
    
    
    
    
class WalletTransaction(models.Model):

    CREDIT = "credit"
    DEBIT = "debit"

    TXN_TYPE_CHOICES = [
        (CREDIT, "Credit"),
        (DEBIT, "Debit"),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txn_type = models.CharField(max_length=10, choices=TXN_TYPE_CHOICES)

    reason = models.CharField(max_length=255)

    order = models.ForeignKey(
        "orders.Order",
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    payment = models.ForeignKey(
        "orders.Payment",
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.txn_type == self.CREDIT else "-"
        return f"{sign}₹{self.amount} ({self.reason})"
