from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse


# ============================================
# ROOT PAGE - Welcome Message
# ============================================
def home_page(request):
    return JsonResponse({
        'status': 'success',
        'message': 'Welcome to YaWallet API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'api_auth': '/api/auth/',
            'api_wallet': '/api/wallet/',
            'api_docs': '/api/docs/',
        },
        'documentation': 'https://yawallet.onrender.com/api/docs/',
        'status': 'online'
    })


def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'YaWallet',
        'version': '1.0.0',
        'timestamp': '2026-07-17 00:00:00'
    })


urlpatterns = [
    path('', home_page, name='home'),  # ← ROOT PAGE
    path('health/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    # Uncomment when you create these apps
    # path('api/transfer/', include('apps.transactions.urls')),
    # path('api/qr/', include('apps.qr.urls')),
    # path('api/bills/', include('apps.bills.urls')),
]
