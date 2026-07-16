from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'YaWallet',
        'version': '1.0.0'
    })


urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    # Uncomment these when you create the URL files
    # path('api/transfer/', include('apps.transactions.urls')),
    # path('api/qr/', include('apps.qr.urls')),
    # path('api/bills/', include('apps.bills.urls')),
]
