from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from decimal import Decimal
from apps.wallet.models import Wallet
from apps.wallet.serializers import WalletSerializer, AddMoneySerializer
from apps.transactions.models import Transaction
from apps.core.permissions import IsNotBlocked, IsKYCVerified, IsWalletActive
from apps.audit.models import AuditLog


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
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        amount = serializer.validated_data['amount']
        payment_method = serializer.validated_data['payment_method']
        
        # For now, just add money directly (no NIFT integration yet)
        with transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(user=request.user)
            wallet.credit(amount, f"Add money via {payment_method}")
            
            # Create transaction record
            transaction_obj = Transaction.objects.create(
                user=request.user,
                transaction_type='ADD_MONEY',
                amount=amount,
                fee=Decimal('0.00'),
                net_amount=amount,
                status='SUCCESS',
                payment_method=payment_method,
                description=f"Add money via {payment_method}"
            )
            
            # Log audit
            AuditLog.objects.create(
                user=request.user,
                action='ADD_MONEY',
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
            'message': 'Money added successfully',
            'data': {
                'transaction_id': transaction_obj.id,
                'amount': amount,
                'new_balance': wallet.balance
            }
        })


class WalletHistoryView(generics.ListAPIView):
    """View for wallet transaction history"""
    
    permission_classes = [IsAuthenticated, IsNotBlocked]
    
    def get_queryset(self):
        from apps.transactions.models import Transaction
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')
    
    def get_serializer_class(self):
        from apps.transactions.serializers import TransactionSerializer
        return TransactionSerializer
