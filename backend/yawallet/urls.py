from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Health check view
def health_check(request):
    return JsonResponse({
        'status': 'healthy',
        'service': 'YaWallet',
        'version': '1.0.0'
    })

schema_view = get_schema_view(
    openapi.Info(
        title="YaWallet API",
        default_version='v1',
        description="YaWallet Mobile Wallet System API",
        terms_of_service="https://www.yawallet.com/terms/",
        contact=openapi.Contact(email="support@yawallet.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API URLs
    path('api/auth/', include('apps.accounts.urls')),
    path('api/wallet/', include('apps.wallet.urls')),
    path('api/transfer/', include('apps.transactions.urls')),
    path('api/qr/', include('apps.qr.urls')),
    path('api/bills/', include('apps.bills.urls')),
    path('api/webhook/', include('yawallet.urls.webhook')),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
