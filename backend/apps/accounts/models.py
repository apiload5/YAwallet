from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import RegexValidator
from django.conf import settings
from apps.core.encryption import encryption_manager
from apps.core.constants import KYC_STATUS_CHOICES, DEVICE_TYPES
from datetime import datetime, timedelta


# ============================================
# CUSTOM USER MANAGER - FIX get_by_natural_key
# ============================================
class UserManager(BaseUserManager):
    """Custom user manager with phone as username"""
    
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('Phone number is required')
        
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone, password, **extra_fields)
    
    # ============================================
    # FIX: Add get_by_natural_key method
    # ============================================
    def get_by_natural_key(self, phone):
        return self.get(phone=phone)


class User(AbstractUser):
    """Custom user model with phone as username"""
    
    username = None  # Remove username field
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')],
        db_index=True
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    
    # Security fields
    transaction_pin = models.CharField(max_length=255, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)
    block_reason = models.TextField(null=True, blank=True)
    blocked_at = models.DateTimeField(null=True, blank=True)
    
    # KYC fields
    kyc_status = models.CharField(
        max_length=20,
        choices=KYC_STATUS_CHOICES,
        default='PENDING'
    )
    kyc_rejection_reason = models.TextField(null=True, blank=True)
    kyc_submitted_at = models.DateTimeField(null=True, blank=True)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Device management
    devices = models.JSONField(default=list)
    max_devices = models.IntegerField(default=3)
    
    # Security
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use custom manager
    objects = UserManager()
    
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['phone', 'is_active']),
            models.Index(fields=['kyc_status', 'is_blocked']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.phone})"
    
    def set_transaction_pin(self, pin: str):
        self.transaction_pin = make_password(pin)
        self.save(update_fields=['transaction_pin'])
    
    def verify_transaction_pin(self, pin: str) -> bool:
        if not self.transaction_pin:
            return False
        return check_password(pin, self.transaction_pin)
    
    def can_add_device(self, device_id: str) -> bool:
        if len(self.devices) >= self.max_devices:
            return False
        return device_id not in self.devices
    
    def add_device(self, device_id: str):
        if self.can_add_device(device_id):
            self.devices.append(device_id)
            self.save(update_fields=['devices'])
            return True
        return False
    
    def remove_device(self, device_id: str):
        if device_id in self.devices:
            self.devices.remove(device_id)
            self.save(update_fields=['devices'])
            return True
        return False
    
    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.now() + timedelta(minutes=15)
        self.save(update_fields=['login_attempts', 'locked_until'])
    
    def reset_login_attempts(self):
        self.login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['login_attempts', 'locked_until'])
    
    def is_locked(self) -> bool:
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        return False
    
    def block(self, reason: str):
        self.is_blocked = True
        self.block_reason = reason
        self.blocked_at = datetime.now()
        self.save(update_fields=['is_blocked', 'block_reason', 'blocked_at'])
    
    def unblock(self):
        self.is_blocked = False
        self.block_reason = None
        self.blocked_at = None
        self.save(update_fields=['is_blocked', 'block_reason', 'blocked_at'])
    
    def get_encrypted_phone(self) -> str:
        if encryption_manager:
            return encryption_manager.encrypt(self.phone)
        return self.phone


class KYCDocument(models.Model):
    """KYC Document model"""
    
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='kyc_documents'
    )
    
    document_type = models.CharField(
        max_length=20,
        choices=[
            ('CNIC_FRONT', 'CNIC Front'),
            ('CNIC_BACK', 'CNIC Back'),
            ('SELFIE', 'Selfie'),
        ]
    )
    
    file_url = models.URLField(max_length=500)
    file_name = models.CharField(max_length=255)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('VERIFIED', 'Verified'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )
    rejection_reason = models.TextField(null=True, blank=True)
    
    verified_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'kyc_documents'
        unique_together = [['user', 'document_type']]
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.document_type}"
