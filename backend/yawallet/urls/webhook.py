from django.urls import path
from apps.payments.views import NIFTWebhookView

urlpatterns = [
    path('nift/', NIFTWebhookView.as_view(), name='nift-webhook'),
]
