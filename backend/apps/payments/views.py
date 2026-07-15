from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.utils import timezone
from apps.transactions.models import Transaction
from apps.wallet.models import Wallet
from apps.audit.models import AuditLog
from apps.payments.services import NIFTService
from apps.core.exceptions import YaWalletException
import logging

logger = logging.getLogger(__name__)

class NIFTWebhookView(APIView):
    """Webhook for NIFT payment updates"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle NIFT webhook"""
        # Verify webhook signature
        signature = request.headers.get('X-Signature')
        nift_service = NIFTService()
        
        # Validate signature (in production)
        # if not nift_service.verify_webhook_signature(request.data, signature):
        #     return Response({'error': 'Invalid signature'}, status=401)
        
        event = request.data.get('event')
        data = request.data.get('data')
        
        if event == 'payment.success':
            return self._handle_payment_success(data)
        elif event == 'payment.failed':
            return self._handle_payment_failed(data)
        elif event == 'transfer.success':
            return self._handle_transfer_success(data)
        elif event == 'transfer.failed':
            return self._handle_transfer_failed(data)
        else:
            return Response({'status': 'ignored'}, status=200)
    
    def _handle_payment_success(self, data):
        """Handle successful payment"""
        transaction_id = data.get('transaction_id')
        reference_id = data.get('reference')
        amount = data.get('amount')
        
        try:
            with transaction.atomic():
                # Get transaction
                transaction_obj = Transaction.objects.select_for_update().get(
                    reference_id=reference_id,
                    status='PENDING'
                )
                
                # Update transaction status
                transaction_obj.complete()
                
                # Credit user's wallet
                wallet = Wallet.objects.select_for_update().get(user=transaction_obj.user)
                wallet.credit(Decimal(amount), f"Add money via NIFT")
                
                # Log audit
                AuditLog.objects.create(
                    user=transaction_obj.user,
                    action='ADD_MONEY_SUCCESS',
                    metadata={
                        'amount': amount,
                        'transaction_id': transaction_obj.id,
                        'reference_id': reference_id
                    }
                )
                
                return Response({'status': 'success'})
                
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {reference_id}")
            return Response({'status': 'error', 'message': 'Transaction not found'}, status=404)
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return Response({'status': 'error', 'message': str(e)}, status=500)
    
    def _handle_payment_failed(self, data):
        """Handle failed payment"""
        reference_id = data.get('reference')
        reason = data.get('reason', 'Payment failed')
        
        try:
            with transaction.atomic():
                transaction_obj = Transaction.objects.select_for_update().get(
                    reference_id=reference_id,
                    status='PENDING'
                )
                transaction_obj.fail(reason)
                
                return Response({'status': 'success'})
                
        except Transaction.DoesNotExist:
            logger.error(f"Transaction not found: {reference_id}")
            return Response({'status': 'error', 'message': 'Transaction not found'}, status=404)
    
    def _handle_transfer_success(self, data):
        """Handle successful transfer"""
        # Similar to payment success but for bank transfers
        pass
    
    def _handle_transfer_failed(self, data):
        """Handle failed transfer"""
        # Similar to payment failed but for bank transfers
        pass
