from django.db import models
from django.conf import settings
from django.db import transaction
from decimal import Decimal
from apps.core.exceptions import InsufficientBalanceError, WalletFrozenError

class Wallet(models.Model):
    """Wallet model for users"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='wallet'
    )
    
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    is_frozen = models.BooleanField(default=False)
    frozen_reason = models.TextField(null=True, blank=True)
    frozen_at = models.DateTimeField(null=True, blank=True)
    
    last_transaction_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wallets'
        indexes = [
            models.Index(fields=['user', 'is_frozen']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - Balance: {self.balance}"
    
    @transaction.atomic
    def credit(self, amount: Decimal, description: str = None) -> bool:
        """Credit amount to wallet"""
        if self.is_frozen:
            raise WalletFrozenError()
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Use select_for_update to lock the row
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        wallet.balance += amount
        wallet.last_transaction_at = models.functions.Now()
        wallet.save(update_fields=['balance', 'last_transaction_at'])
        
        return True
    
    @transaction.atomic
    def debit(self, amount: Decimal, description: str = None) -> bool:
        """Debit amount from wallet"""
        if self.is_frozen:
            raise WalletFrozenError()
        
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Use select_for_update to lock the row
        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        
        if wallet.balance < amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Available: {wallet.balance}, Required: {amount}"
            )
        
        wallet.balance -= amount
        wallet.last_transaction_at = models.functions.Now()
        wallet.save(update_fields=['balance', 'last_transaction_at'])
        
        return True
    
    @transaction.atomic
    def transfer(self, to_wallet, amount: Decimal, description: str = None):
        """Transfer amount to another wallet"""
        # Debit from source
        self.debit(amount, description)
        
        # Credit to destination
        to_wallet.credit(amount, description)
        
        return True
    
    def freeze(self, reason: str):
        """Freeze wallet"""
        self.is_frozen = True
        self.frozen_reason = reason
        self.frozen_at = models.functions.Now()
        self.save(update_fields=['is_frozen', 'frozen_reason', 'frozen_at'])
    
    def unfreeze(self):
        """Unfreeze wallet"""
        self.is_frozen = False
        self.frozen_reason = None
        self.frozen_at = None
        self.save(update_fields=['is_frozen', 'frozen_reason', 'frozen_at'])
