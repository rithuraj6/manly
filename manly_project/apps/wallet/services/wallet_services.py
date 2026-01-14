from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.orders.models import Payment

from apps.wallet.models import Wallet,WalletTransaction


@transaction.atomic
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


@transaction.atomic
def pay_order_using_wallet(user,order):
    
    if order is None:
        raise ValueError("Order must be created before wallet payment")
    

    
    wallet = Wallet.objects.select_for_update().get(user=user)

    if wallet.balance < order.total_amount:
        raise ValueError("Insufficient wallet balance")
    
    wallet.balance -= order.total_amount
    wallet.save(update_fields=["balance"])

    
   


    payment = Payment.objects.create(
        user=user,
        payment_method='wallet',
        amount=order.total_amount,
        status='success',
        address_snapshot=order.address_snapshot
    )        
    
    
    
    WalletTransaction.objects.create(
        wallet=wallet,amount=order.total_amount,
        txn_type=WalletTransaction.DEBIT,
        reason=f'Order payment({order.order_id})',
        order=order,
        payment=payment,
        
        
    )
    
    
    order.is_paid = True
    order.payment_method = "wallet"
    order.save(update_fields=["is_paid", "payment_method"])
    
    return payment



@transaction.atomic
def refund_to_wallet(*, user, amount, reason, order=None):
    """
    Credits refund amount to user's wallet.
    Always used for cancel / return refunds.
    """

    wallet, _ = Wallet.objects.get_or_create(user=user)

    wallet.balance += Decimal(amount)
    wallet.save(update_fields=["balance"])

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=Decimal(amount),
        txn_type=WalletTransaction.CREDIT,
        reason=reason,
        order=order,
    )

    Payment.objects.create(
        user=user,
        payment_method="wallet",
        amount=Decimal(amount),
        status="success",
    )