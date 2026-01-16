from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.orders.models import Order
from apps.wallet.services.wallet_services import credit_admin_wallet
from .models import Wallet

User  = settings.AUTH_USER_MODEL

@receiver(post_save,sender=User)
def create_wallet(sender,instance,created,**kwargs):
    if created:
        Wallet.objects.create(user=instance)
        




  
        
    