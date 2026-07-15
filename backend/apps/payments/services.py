import hashlib
import hmac
import json
import requests
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from apps.core.exceptions import YaWalletException
import logging

logger = logging.getLogger(__name__)

class NIFTService:
    """NIFT ePay API Integration"""
    
    def __init__(self):
        self.api_url = settings.NIFT_API_URL
        self.api_key = settings.NIFT_API_KEY
        self.api_secret = settings.NIFT_API_SECRET
        self.webhook_secret = settings.NIFT_WEBHOOK_SECRET
        
    def _generate_signature(self, payload: dict) -> str:
        """Generate HMAC-SHA256 signature"""
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.api_secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, endpoint: str, method: str = 'POST', data: dict = None) -> dict:
        """Make HTTP request to NIFT API"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key,
            'X-Signature': self._generate_signature(data or {}),
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"NIFT API error: {e}")
            raise YaWalletException(f"Payment service error: {str(e)}")
    
    def initiate_payment(self, amount: Decimal, payment_method: str, user: 'User', metadata: dict = None) -> dict:
        """Initiate payment via NIFT"""
        # For demo/testing, return mock response
        if settings.DEBUG or not self.api_key:
            return self._mock_payment_response(amount)
        
        payload = {
            'amount': str(amount),
            'payment_method': payment_method,
            'customer_phone': user.phone,
            'customer_name': user.full_name,
            'customer_email': user.email or '',
            'reference': f"PAY_{user.id}_{timezone.now().timestamp()}",
            'metadata': metadata or {},
            'return_url': f"{settings.BASE_URL}/payment/callback/"
        }
        
        response = self._make_request('/payments/initiate', 'POST', payload)
        return response
    
    def verify_payment(self, transaction_id: str) -> dict:
        """Verify payment status"""
        if settings.DEBUG or not self.api_key:
            return {
                'status': 'SUCCESS',
                'transaction_id': transaction_id,
                'amount': '100.00',
                'reference': f"REF_{transaction_id}"
            }
        
        response = self._make_request(f'/payments/{transaction_id}/verify', 'GET')
        return response
    
    def initiate_ibft_transfer(self, amount: Decimal, bank_account: 'BankAccount', user: 'User') -> dict:
        """Initiate IBFT transfer"""
        if settings.DEBUG or not self.api_key:
            return self._mock_ibft_response(amount)
        
        payload = {
            'amount': str(amount),
            'bank_account': {
                'account_number': bank_account.account_number,
                'account_title': bank_account.account_title,
                'bank_code': bank_account.bank_code,
                'iban': bank_account.iban,
            },
            'customer_phone': user.phone,
            'customer_name': user.full_name,
            'reference': f"IBFT_{user.id}_{timezone.now().timestamp()}"
        }
        
        response = self._make_request('/ibft/transfer', 'POST', payload)
        return response
    
    def pay_bill(self, biller_id: str, consumer_number: str, amount: Decimal, user: 'User') -> dict:
        """Pay bill via NIFT"""
        if settings.DEBUG or not self.api_key:
            return self._mock_bill_payment_response()
        
        payload = {
            'biller_id': biller_id,
            'consumer_number': consumer_number,
            'amount': str(amount),
            'customer_phone': user.phone,
            'customer_name': user.full_name,
            'reference': f"BILL_{user.id}_{timezone.now().timestamp()}"
        }
        
        response = self._make_request('/bills/pay', 'POST', payload)
        return response
    
    def _mock_payment_response(self, amount: Decimal) -> dict:
        """Mock payment response for testing"""
        import uuid
        return {
            'status': 'PENDING',
            'transaction_id': str(uuid.uuid4()),
            'payment_url': 'https://mock-nift.com/pay/12345',
            'amount': str(amount),
            'reference': f"MOCK_{uuid.uuid4().hex[:8]}"
        }
    
    def _mock_ibft_response(self, amount: Decimal) -> dict:
        """Mock IBFT response for testing"""
        import uuid
        return {
            'status': 'SUCCESS',
            'transaction_id': str(uuid.uuid4()),
            'amount': str(amount),
            'reference': f"IBFT_{uuid.uuid4().hex[:8]}",
            'message': 'Transfer initiated successfully'
        }
    
    def _mock_bill_payment_response(self) -> dict:
        """Mock bill payment response for testing"""
        import uuid
        return {
            'status': 'SUCCESS',
            'transaction_id': str(uuid.uuid4()),
            'reference': f"BILL_{uuid.uuid4().hex[:8]}",
            'message': 'Bill paid successfully'
        }

class BankService:
    """Bank account service"""
    
    @staticmethod
    def get_bank_list():
        """Get list of supported banks"""
        return [
            {'code': 'HBL', 'name': 'Habib Bank Limited'},
            {'code': 'MCB', 'name': 'MCB Bank Limited'},
            {'code': 'UBL', 'name': 'United Bank Limited'},
            {'code': 'ABL', 'name': 'Allied Bank Limited'},
            {'code': 'MEEZAN', 'name': 'Meezan Bank Limited'},
            {'code': 'JS', 'name': 'JS Bank Limited'},
            {'code': 'FAYSAL', 'name': 'Faysal Bank Limited'},
            {'code': 'SCB', 'name': 'Standard Chartered Bank'},
            {'code': 'CITI', 'name': 'Citibank N.A.'},
            {'code': 'BOP', 'name': 'Bank of Punjab'},
            {'code': 'NBP', 'name': 'National Bank of Pakistan'},
        ]
