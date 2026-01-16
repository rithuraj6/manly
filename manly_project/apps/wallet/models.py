from django.conf import settings
from django.db import models
from apps.orders.models import Order, OrderItem

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
    order_item = models.ForeignKey(
    "orders.OrderItem",
    null=True,
    blank=True,
    on_delete=models.SET_NULL
    )

    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order_item"],
                condition=models.Q(txn_type="credit"),
                name="unique_refund_per_order_item"
            )
        ]
        
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.txn_type == self.CREDIT else "-"
        return f"{sign}₹{self.amount} ({self.reason})"









class AdminWallet(models.Model):
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    updated_at = models.DateTimeField(auto_now=True)
    
   

    def __str__(self):
        return f"Admin Wallet ₹{self.balance}"
    

class AdminWalletTransaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('credit',"Credit"),
        ('debit','Debit')
    )
    
    
    wallet = models.ForeignKey(AdminWallet,on_delete=models.CASCADE,related_name='transactions')
    
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPE_CHOICES
    )
    
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    
    order = models.ForeignKey(Order,on_delete = models.SET_NULL,null =True,blank=True)
    
    order_item = models.ForeignKey(OrderItem,on_delete=models.SET_NULL,null=True,blank=True)
    
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null= True)
    
    description = models.CharField(max_length=223)
    
    created_at = models.DateTimeField(auto_now_add = True)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(transaction_type="credit"),
                name="unique_admin_credit_per_order"
            )
        ]
        
        
    def __str__(self):
        return   f"{self.transaction_type.upper()} ₹{self.amount}"
        