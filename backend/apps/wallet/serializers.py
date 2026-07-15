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
    card_token = serializers.CharField(required=False, allow_blank=True)
    bank_account_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate(self, data):
        """Validate amount and payment method"""
        if data['amount'] <= Decimal('0'):
            raise serializers.ValidationError("Amount must be greater than 0")
        
        if data['payment_method'] == 'CARD' and not data.get('card_token'):
            raise serializers.ValidationError("Card token is required for card payment")
        
        return data
