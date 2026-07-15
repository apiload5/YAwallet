from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from apps.accounts.models import User, KYCDocument
from apps.core.exceptions import InvalidPinError, UserBlockedError, KYCRequiredError
from apps.core.encryption import encryption_manager
import re

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['phone', 'full_name', 'email', 'password']
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if not re.match(r'^\+?1?\d{9,15}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already registered")
        
        return value
    
    def create(self, validated_data):
        """Create user with hashed password"""
        user = User.objects.create_user(
            phone=validated_data['phone'],
            full_name=validated_data['full_name'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    device_id = serializers.CharField()
    
    def validate(self, data):
        """Validate login credentials"""
        phone = data.get('phone')
        password = data.get('password')
        device_id = data.get('device_id')
        
        user = User.objects.filter(phone=phone).first()
        
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        if user.is_locked():
            raise serializers.ValidationError("Account is locked. Try again after 15 minutes.")
        
        if user.is_blocked:
            raise UserBlockedError(f"Account blocked: {user.block_reason}")
        
        if not user.check_password(password):
            user.increment_login_attempts()
            raise serializers.ValidationError("Invalid credentials")
        
        # Reset login attempts on successful login
        user.reset_login_attempts()
        
        # Handle device management
        if not user.can_add_device(device_id) and device_id not in user.devices:
            raise serializers.ValidationError("Device limit exceeded")
        
        if device_id not in user.devices:
            user.add_device(device_id)
        
        data['user'] = user
        return data

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'full_name', 'email', 
            'kyc_status', 'is_blocked', 'is_active',
            'created_at', 'last_login'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']

class KYCDocumentSerializer(serializers.ModelSerializer):
    """Serializer for KYC documents"""
    
    class Meta:
        model = KYCDocument
        fields = [
            'id', 'document_type', 'file_url', 'file_name',
            'status', 'rejection_reason', 'verified_at', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'rejection_reason', 'verified_at', 'created_at']

class KYCSubmissionSerializer(serializers.Serializer):
    """Serializer for KYC submission"""
    
    cnic_front = serializers.URLField(required=True)
    cnic_back = serializers.URLField(required=True)
    selfie = serializers.URLField(required=True)
    
    def validate(self, data):
        """Validate KYC documents"""
        user = self.context['request'].user
        
        if user.kyc_status == 'APPROVED':
            raise serializers.ValidationError("KYC already approved")
        
        # Check if documents are already submitted
        existing = KYCDocument.objects.filter(user=user)
        if existing.exists():
            raise serializers.ValidationError("KYC documents already submitted")
        
        return data

class PinVerificationSerializer(serializers.Serializer):
    """Serializer for PIN verification"""
    
    pin = serializers.CharField(min_length=4, max_length=4)
    
    def validate_pin(self, value):
        """Validate PIN is numeric"""
        if not value.isdigit():
            raise serializers.ValidationError("PIN must be numeric")
        return value

class SetTransactionPinSerializer(serializers.Serializer):
    """Serializer for setting transaction PIN"""
    
    new_pin = serializers.CharField(min_length=4, max_length=4)
    confirm_pin = serializers.CharField(min_length=4, max_length=4)
    
    def validate(self, data):
        """Validate PINs match"""
        if data['new_pin'] != data['confirm_pin']:
            raise serializers.ValidationError("PINs do not match")
        
        if not data['new_pin'].isdigit():
            raise serializers.ValidationError("PIN must be numeric")
        
        return data

class VerifyTransactionPinSerializer(serializers.Serializer):
    """Serializer for verifying transaction PIN"""
    
    pin = serializers.CharField(min_length=4, max_length=4)
    
    def validate(self, data):
        """Validate PIN"""
        user = self.context['request'].user
        
        if not user.transaction_pin:
            raise serializers.ValidationError("Transaction PIN not set")
        
        if not user.verify_transaction_pin(data['pin']):
            raise InvalidPinError()
        
        return data
