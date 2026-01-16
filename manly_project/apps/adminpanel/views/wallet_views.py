from django.shortcuts import render
from django.db.models import Sum
from decimal import Decimal
from django.core.paginator import Paginator

from apps.wallet.services.wallet_services import get_admin_wallet


def admin_wallet_dashboard(request):
    wallet = get_admin_wallet()

    total_earned = (
        wallet.transactions.filter(transaction_type="credit")
        .aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )

    total_refunded = (
        wallet.transactions.filter(transaction_type="debit")
        .aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
    )
    
    income_qs = wallet.transactions.filter(
        transaction_type="credit"
    ).order_by("-created_at")

    refund_qs = wallet.transactions.filter(
        transaction_type="debit"
    ).order_by("-created_at")
    
    income_paginator = Paginator(income_qs, 10)   
    refund_paginator = Paginator(refund_qs, 10)

    income_page_number = request.GET.get("income_page")
    refund_page_number = request.GET.get("refund_page")

    income_page = income_paginator.get_page(income_page_number)
    refund_page = refund_paginator.get_page(refund_page_number)


    return render(
        request,
        "adminpanel/wallet/wallet_dashboard.html",
        {
            "wallet": wallet,
            "current_balance": wallet.balance,
            "total_earned": total_earned,
            "total_refunded": total_refunded,

            "income_list": income_page,
            "refund_list": refund_page,

            "income_page": income_page,
            "refund_page": refund_page,
        },
    )
