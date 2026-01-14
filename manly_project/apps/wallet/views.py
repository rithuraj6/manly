from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.wallet.models import Wallet,WalletTransaction


@login_required
def wallet_page(request):
    
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    
    transactions=(
        WalletTransaction.objects.filter(wallet=wallet).select_related('order')
        .order_by('-created_at')
        
    )
    
    
    return render(
        request,
        "wallet/wallet.html",
        {
            "wallet": wallet,
            "transactions": transactions,
        }
    )
