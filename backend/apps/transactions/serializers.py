from rest_framework import serializers
from apps.transactions.models import Transaction
from apps.accounts.serializers import UserSerializer
from decimal import Decimal

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    
    user = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'amount', 'fee', 'net_amount',
            'status', 'payment_method', 'reference_id',
            'recipient', 'description', 'metadata',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class P2PTransferSerializer(serializers.Serializer):
    """Serializer for P2P transfer"""
    
    recipient_phone = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    pin = serializers.CharField(min_length=4, max_length=4)
    description = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate transfer"""
        user = self.context['request'].user
        amount = data['amount']
        
        # Check user KYC
        if user.kyc_status != 'APPROVED':
            raise serializers.ValidationError("KYC verification required")
        
        # Check wallet balance
        if user.wallet.balance < amount:
            raise serializers.ValidationError("Insufficient balance")
        
        # Check recipient exists
        try:
            recipient = User.objects.get(phone=data['recipient_phone'])
            if recipient == user:
                raise serializers.ValidationError("Cannot transfer to yourself")
            if recipient.is_blocked:
                raise serializers.ValidationError("Recipient account is blocked")
            if recipient.wallet.is_frozen:
                raise serializers.ValidationError("Recipient wallet is frozen")
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient not found")
        
        data['recipient'] = recipient
        return data
