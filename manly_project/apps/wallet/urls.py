from django.urls import path
from .views import wallet_page,create_wallet_topup_order,verify_wallet_payment


urlpatterns = [
    path("", wallet_page, name="wallet_page"),
    path("topup/create/", create_wallet_topup_order, name="create_wallet_topup_order"),
    path("topup/verify/", verify_wallet_payment, name="verify_wallet_payment"),
]