from rest_framework import serializers
from apps.transactions.models import Transaction
from apps.accounts.serializers import UserSerializer


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
