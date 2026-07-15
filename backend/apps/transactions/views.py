from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from apps.transactions.models import Transaction
from apps.transactions.serializers import TransactionSerializer, P2PTransferSerializer
from apps.wallet.models import Wallet
from apps.core.permissions import IsNotBlocked, IsKYCVerified, IsWalletActive, HasTransactionPin
from apps.core.exceptions import InsufficientBalanceError, InvalidPinError
from apps.core.throttling import TransferRateThrottle
from apps.audit.models import AuditLog
from apps.notifications.services import NotificationService
from drf_yasg.utils import swagger_auto_schema

class P2PTransferView(generics.GenericAPIView):
    """P2P transfer view"""
    
    serializer_class = P2PTransferSerializer
    permission_classes = [
        IsAuthenticated, IsNotBlocked, IsKYCVerified, 
        IsWalletActive, HasTransactionPin
    ]
    throttle_classes = [TransferRateThrottle]
    
    @swagger_auto_schema(
        operation_description="Transfer money to another user",
        request_body=P2PTransferSerializer
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        recipient = serializer.validated_data['recipient']
        amount = serializer.validated_data['amount']
        pin = serializer.validated_data['pin']
        description = serializer.validated_data.get('description', '')
        
        # Verify PIN
        if not user.verify_transaction_pin(pin):
            raise InvalidPinError()
        
        # Calculate fee
        fee_percent = Decimal(str(settings.TRANSACTION_FEE_PERCENT / 100))
        min_fee = Decimal(str(settings.TRANSACTION_FEE_MIN))
        fee = amount * fee_percent
        if fee < min_fee:
            fee = min_fee
        
        net_amount = amount - fee
        
        try:
            with transaction.atomic():
                # Get wallets with lock
                sender_wallet = Wallet.objects.select_for_update().get(user=user)
                recipient_wallet = Wallet.objects.select_for_update().get(user=recipient)
                
                # Check balance
                if sender_wallet.balance < amount:
                    raise InsufficientBalanceError()
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    user=user,
                    transaction_type='P2P_TRANSFER',
                    amount=amount,
                    fee=fee,
                    net_amount=net_amount,
                    recipient=recipient,
                    description=description,
                    status='PENDING'
                )
                
                # Perform transfer
                sender_wallet.debit(amount)
                recipient_wallet.credit(net_amount)
                
                # Complete transaction
                transaction_obj.complete()
                
                # Create audit log
                AuditLog.objects.create(
                    user=user,
                    action='P2P_TRANSFER',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    metadata={
                        'amount': str(amount),
                        'fee': str(fee),
                        'recipient': recipient.phone,
                        'transaction_id': transaction_obj.id
                    }
                )
                
                # Send notifications
                NotificationService.send_transfer_notification(
                    user=user,
                    recipient=recipient,
                    amount=amount,
                    fee=fee,
                    transaction_id=transaction_obj.id
                )
                
                return Response({
                    'success': True,
                    'message': 'Transfer successful',
                    'data': {
                        'transaction_id': transaction_obj.id,
                        'amount': amount,
                        'fee': fee,
                        'net_amount': net_amount,
                        'recipient': {
                            'name': recipient.full_name,
                            'phone': recipient.phone
                        },
                        'new_balance': sender_wallet.balance
                    }
                })
                
        except Exception as e:
            return Response({
                'success': False,
                'error': {'message': str(e)}
            }, status=status.HTTP_400_BAD_REQUEST)
