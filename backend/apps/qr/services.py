import re
from decimal import Decimal
from django.db import transaction
from apps.qr.models import QRCode
from apps.transactions.models import Transaction
from apps.wallet.models import Wallet
from apps.core.exceptions import YaWalletException

class QRService:
    """QR code service"""
    
    @staticmethod
    def generate_till_id():
        """Generate unique till ID"""
        import uuid
        return str(uuid.uuid4())[:10].upper()
    
    @staticmethod
    def parse_qr_data(qr_data: str) -> dict:
        """Parse QR code data"""
        # Format: ya://pay?tillid=12345&amount=100
        pattern = r'^ya://pay\?tillid=([A-Z0-9]+)(?:&amount=([0-9.]+))?$'
        match = re.match(pattern, qr_data)
        
        if not match:
            raise YaWalletException("Invalid QR code format")
        
        result = {
            'till_id': match.group(1),
            'amount': Decimal(match.group(2)) if match.group(2) else None
        }
        
        return result
    
    @staticmethod
    def process_qr_payment(qr_data: str, payer: 'User', pin: str) -> dict:
        """Process QR payment"""
        # Parse QR data
        parsed = QRService.parse_qr_data(qr_data)
        till_id = parsed['till_id']
        amount = parsed['amount']
        
        # Get QR code
        try:
            qr_code = QRCode.objects.select_related('user__wallet').get(
                till_id=till_id,
                is_active=True
            )
        except QRCode.DoesNotExist:
            raise YaWalletException("Invalid QR code")
        
        # Check if amount is specified in QR
        if not amount:
            raise YaWalletException("Amount not specified in QR code")
        
        # Get payer and payee
        payee = qr_code.user
        
        # Check if payer is not payee
        if payer == payee:
            raise YaWalletException("Cannot pay to yourself")
        
        # Verify PIN
        if not payer.verify_transaction_pin(pin):
            raise YaWalletException("Invalid PIN")
        
        # Process payment
        with transaction.atomic():
            # Get wallets with lock
            payer_wallet = Wallet.objects.select_for_update().get(user=payer)
            payee_wallet = Wallet.objects.select_for_update().get(user=payee)
            
            # Check balance
            if payer_wallet.balance < amount:
                raise YaWalletException("Insufficient balance")
            
            # Create transaction
            transaction_obj = Transaction.objects.create(
                user=payer,
                transaction_type='QR_PAYMENT',
                amount=amount,
                fee=Decimal('0.00'),
                net_amount=amount,
                recipient=payee,
                qr_code=qr_code,
                description=f"QR payment to {payee.full_name}",
                status='PENDING'
            )
            
            # Perform transfer
            payer_wallet.debit(amount)
            payee_wallet.credit(amount)
            
            # Complete transaction
            transaction_obj.complete()
            
            return {
                'success': True,
                'transaction_id': transaction_obj.id,
                'amount': amount,
                'payee': {
                    'name': payee.full_name,
                    'phone': payee.phone
                },
                'new_balance': payer_wallet.balance
            }
