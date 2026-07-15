from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.constants import TRANSACTION_TYPES, TRANSACTION_STATUS

class Transaction(models.Model):
    """Transaction model for all transactions"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        db_index=True
    )
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    net_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    status = models.CharField(
        max_length=20,
        choices=TRANSACTION_STATUS,
        default='PENDING',
        db_index=True
    )
    
    # P2P transfer fields
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_transactions'
    )
    
    # Payment fields
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    
    # Bank transfer fields
    bank_account = models.ForeignKey(
        'payments.BankAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # QR fields
    qr_code = models.ForeignKey(
        'qr.QRCode',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Bill payment fields
    biller = models.ForeignKey(
        'bills.Biller',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    bill_reference = models.CharField(max_length=255, null=True, blank=True)
    
    # Description and metadata
    description = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict)
    
    # Timestamps
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['reference_id']),
            models.Index(fields=['transaction_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.status}"
    
    def calculate_fee(self) -> Decimal:
        """Calculate transaction fee"""
        from django.conf import settings
        
        fee_percent = Decimal(str(settings.TRANSACTION_FEE_PERCENT / 100))
        min_fee = Decimal(str(settings.TRANSACTION_FEE_MIN))
        
        fee = self.amount * fee_percent
        if fee < min_fee:
            fee = min_fee
        
        return fee.quantize(Decimal('0.01'))
    
    def complete(self):
        """Mark transaction as completed"""
        self.status = 'SUCCESS'
        self.completed_at = models.functions.Now()
        self.save(update_fields=['status', 'completed_at'])
    
    def fail(self, reason: str = None):
        """Mark transaction as failed"""
        self.status = 'FAILED'
        self.metadata['failure_reason'] = reason
        self.save(update_fields=['status', 'metadata'])
