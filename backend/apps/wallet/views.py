from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from apps.wallet.models import Wallet
from apps.wallet.serializers import WalletSerializer, AddMoneySerializer
from apps.transactions.models import Transaction
from apps.payments.services import NIFTService
from apps.core.permissions import IsNotBlocked, IsKYCVerified, IsWalletActive
from apps.core.exceptions import KYCRequiredError, WalletFrozenError
from apps.audit.models import AuditLog
from drf_yasg.utils import swagger_auto_schema

class WalletBalanceView(generics.RetrieveAPIView):
    """View for wallet balance"""
    
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated, IsNotBlocked, IsKYCVerified]
    
    def get_object(self):
        return self.request.user.wallet

class AddMoneyView(generics.GenericAPIView):
    """View for adding money to wallet"""
    
    serializer_class = AddMoneySerializer
    permission_classes = [IsAuthenticated, IsNotBlocked, IsKYCVerified, IsWalletActive]
    
    @swagger_auto_schema(
        operation_description="Add money to wallet",
        request_body=AddMoneySerializer
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        
        # Initialize NIFT service
        nift_service = NIFTService()
        
        try:
            # Process payment via NIFT
            payment_result = nift_service.initiate_payment(
                amount=amount,
                payment_method=payment_method,
                user=request.user,
                metadata={
                    'card_token': serializer.validated_data.get('card_token'),
                    'bank_account_id': serializer.validated_data.get('bank_account_id'),
                }
            )
            
            # Create transaction
            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    user=request.user,
                    transaction_type='ADD_MONEY',
                    amount=amount,
                    fee=Decimal('0.00'),
                    status='PENDING',
                    payment_method=payment_method,
                    reference_id=payment_result.get('transaction_id'),
                    metadata=payment_result,
                    description=f"Add money via {payment_method}"
                )
                
                # Log audit
                AuditLog.objects.create(
                    user=request.user,
                    action='ADD_MONEY_INITIATED',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    metadata={
                        'amount': str(amount),
                        'payment_method': payment_method,
                        'transaction_id': transaction_obj.id
                    }
                )
            
            return Response({
                'success': True,
                'message': 'Payment initiated successfully',
                'data': {
                    'transaction_id': transaction_obj.id,
                    'amount': amount,
                    'status': 'PENDING',
                    'payment_url': payment_result.get('payment_url'),
                    'reference_id': payment_result.get('transaction_id')
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)

class WalletHistoryView(generics.ListAPIView):
    """View for wallet transaction history"""
    
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        from apps.transactions.serializers import TransactionSerializer
        return TransactionSerializer
