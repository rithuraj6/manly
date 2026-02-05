from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.orders.models import Payment
from apps.wallet.models import Wallet, WalletTransaction, AdminWalletTransaction

from apps.wallet.models import AdminWallet
from django.db.models import Sum


def get_admin_wallet():
    wallet, _ = AdminWallet.objects.get_or_create(id=1)
    return wallet



@transaction.atomic
def credit_wallet(*, wallet: Wallet, amount: Decimal, reason: str, order=None, payment=None):
    if amount <= 0:
        raise ValidationError("Credit amount must be positive")

    wallet.balance += amount
    wallet.save(update_fields=["balance"])

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        txn_type=WalletTransaction.CREDIT,
        reason=reason,
        order=order,
        payment=payment,
    )

    return wallet.balance

@transaction.atomic
def debit_admin_wallet(order_item, amount):
    wallet = get_admin_wallet()

    AdminWalletTransaction.objects.create(
        wallet=wallet,
        transaction_type="debit",
        amount=amount,
        order=order_item.order,
        order_item=order_item,
        user=order_item.order.user,
        description=f"Refund issued - {order_item.order.order_id}",
    )

    wallet.balance -= amount
    wallet.save(update_fields=["balance"])





@transaction.atomic
def pay_order_using_wallet(*, user, order):
    if not order:
        raise ValueError("Order must exist before wallet payment")

    total_amount = (
        order.items.aggregate(total=Sum("final_price_paid"))["total"]
        or Decimal("0.00")
    )

    wallet = Wallet.objects.select_for_update().get(user=user)

    if wallet.balance < total_amount:
        raise ValueError("Insufficient wallet balance")

    payment = Payment.objects.create(
        user=user,
        payment_method="wallet",
        amount=total_amount,
        status="success",
        address_snapshot=order.address_snapshot,
        order=order,
    )

    debit_wallet(
        wallet=wallet,
        amount=total_amount,
        reason=f"Order payment ({order.order_id})",
        order=order,
        payment=payment,
    )

    order.is_paid = True
    order.payment_method = "wallet"
    order.save(update_fields=["is_paid", "payment_method"])

    credit_admin_wallet(order=order, amount=total_amount)

    return payment






@transaction.atomic
def refund_to_wallet(*, user, order_item, amount, reason):
  

    wallet, _ = Wallet.objects.get_or_create(user=user)

  
    credit_wallet(
        wallet=wallet,
        amount=Decimal(amount),
        reason=reason,
        order=order_item.order,
    )
    debit_admin_wallet(
        order_item=order_item,
        amount= Decimal(amount),
    )


@transaction.atomic
def credit_admin_wallet(*, order, amount: Decimal):
    wallet = AdminWallet.objects.select_for_update().get(id=1)

    if AdminWalletTransaction.objects.filter(
        order=order,
        transaction_type="credit"
    ).exists():
        return 

    AdminWalletTransaction.objects.create(
        wallet=wallet,
        transaction_type="credit",
        amount=amount,
        order=order,
        user=order.user,
        description=f"Order payment received - {order.order_id}",
    )

    wallet.balance += amount
    wallet.save(update_fields=["balance"])

    

@transaction.atomic
def debit_wallet(*, wallet: Wallet, amount: Decimal, reason: str, order=None, payment=None):
    if amount <= 0:
        raise ValidationError("Debit amount must be positive")

    if wallet.balance < amount:
        raise ValueError("Insufficient wallet balance")

    wallet.balance -= amount
    wallet.save(update_fields=["balance"])

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        txn_type=WalletTransaction.DEBIT,
        reason=reason,
        order=order,
        payment=payment,
    )

    return wallet.balance


