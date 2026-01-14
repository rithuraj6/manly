from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError


from apps.wallet.models import Wallet,WalletTransaction


@trasaction.atomic
def credit_wallet(
    *,wallet:Wallet,
    amount:Decimal,
    reason:str,
    order =None,
    payment=None
):
    if amount <=0:
        raise ValidationError('credit amount must be positive')
    
    wallet.balance += amount
    wallet.save(update_fields=['balance'])
    
    WalletTransaction.objects.create(wallet=wallet,amount=amount,
                                    taxn_type=WalletTransaction.CREDIT,reason=reason,
                                    order=order,payment=payment)
    
    return wallet.balance




@transaction.atomic

def debit_wallet(
    *,wallet:Wallet,amount:Decimal,reason:str,order=None
):
    
    
    if amount <=0:
        raise ValidationError("Debit amount must be positive")
    
    if wallet.balance<amount:
        raise ValidationError('Insufficient Wallet Balance')
    
    
    
    wallet.balance -=amount
    wallet.save(update_fields=['balance'])
    
    WalletTransaction.objects.create(
        wallet=wallet,amount=amount,txn_type=WalletTransaction.DEBIT,
        reason=reason,order=order
    )
    
    
    return wallet.balance


