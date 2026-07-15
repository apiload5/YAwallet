from django.urls import path
from apps.accounts.views import (
    RegisterView, FirebaseLoginView, UserProfileView,
    KYCDocumentView, SetTransactionPinView, VerifyTransactionPinView,
    LogoutView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('firebase-login/', FirebaseLoginView.as_view(), name='firebase-login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('kyc/', KYCDocumentView.as_view(), name='kyc'),
    path('set-pin/', SetTransactionPinView.as_view(), name='set-pin'),
    path('verify-pin/', VerifyTransactionPinView.as_view(), name='verify-pin'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
