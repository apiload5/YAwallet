from django.urls import path
from apps.wallet.views import WalletBalanceView, AddMoneyView, WalletHistoryView

app_name = 'wallet'

urlpatterns = [
    path('balance/', WalletBalanceView.as_view(), name='balance'),
    path('add-money/', AddMoneyView.as_view(), name='add-money'),
    path('history/', WalletHistoryView.as_view(), name='history'),
]
