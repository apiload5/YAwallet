from rest_framework import serializers
from apps.wallet.models import Wallet
from decimal import Decimal


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet"""
    
    class Meta:
        model = Wallet
        fields = [
            'id', 'balance', 'is_frozen', 'frozen_reason',
            'last_transaction_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'balance', 'created_at', 'updated_at']


class AddMoneySerializer(serializers.Serializer):
    """Serializer for adding money"""
    
    amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))
    payment_method = serializers.ChoiceField(choices=['CARD', 'BANK', 'EASYPAISA', 'JAZZCASH'])
    
    def validate_amount(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
