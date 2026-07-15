from django.db import models
from django.conf import settings
from decimal import Decimal

class Biller(models.Model):
    """Billers model for bill payments"""
    
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    category = models.CharField(
        max_length=50,
        choices=[
            ('ELECTRICITY', 'Electricity'),
            ('GAS', 'Gas'),
            ('INTERNET', 'Internet'),
            ('WATER', 'Water'),
            ('TELEPHONE', 'Telephone'),
            ('EDUCATION', 'Education'),
            ('OTHER', 'Other'),
        ]
    )
    logo = models.ImageField(upload_to='billers/', null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, null=True, blank=True)
    color = models.CharField(max_length=20, null=True, blank=True)
    
    # Configuration
    consumer_number_format = models.CharField(max_length=100, null=True, blank=True)
    requires_amount = models.BooleanField(default=True)
    
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'billers'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]
    
    def __str__(self):
        return self.name

class BillPayment(models.Model):
    """Bill payment record"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='bill_payments'
    )
    
    biller = models.ForeignKey(
        Biller,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    
    consumer_number = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    fee = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'))
    net_amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING',
        db_index=True
    )
    
    reference_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    transaction = models.ForeignKey(
        'transactions.Transaction',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bill_payment'
    )
    
    metadata = models.JSONField(default=dict)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bill_payments'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['biller', 'status']),
            models.Index(fields=['reference_id']),
        ]
    
    def __str__(self):
        return f"{self.biller.name} - {self.amount}"
