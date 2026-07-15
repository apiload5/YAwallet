from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class YaWalletException(Exception):
    """Base exception for YaWallet"""
    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class InsufficientBalanceError(YaWalletException):
    def __init__(self, message="Insufficient balance"):
        super().__init__(message, code="INSUFFICIENT_BALANCE", status_code=400)

class KYCRequiredError(YaWalletException):
    def __init__(self, message="KYC verification required"):
        super().__init__(message, code="KYC_REQUIRED", status_code=403)

class WalletFrozenError(YaWalletException):
    def __init__(self, message="Wallet is frozen"):
        super().__init__(message, code="WALLET_FROZEN", status_code=403)

class UserBlockedError(YaWalletException):
    def __init__(self, message="User is blocked"):
        super().__init__(message, code="USER_BLOCKED", status_code=403)

class InvalidPinError(YaWalletException):
    def __init__(self, message="Invalid PIN"):
        super().__init__(message, code="INVALID_PIN", status_code=400)

class DeviceLimitError(YaWalletException):
    def __init__(self, message="Device limit exceeded"):
        super().__init__(message, code="DEVICE_LIMIT_EXCEEDED", status_code=400)

def custom_exception_handler(exc, context):
    """Custom exception handler for YaWallet"""
    
    # Get the response from DRF's default handler
    response = exception_handler(exc, context)
    
    # If there's a response, we can customize it
    if response is not None:
        data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'code', 'ERROR'),
                'message': str(exc),
                'status_code': response.status_code
            }
        }
        
        # Include field errors if present
        if hasattr(exc, 'detail') and hasattr(exc.detail, 'items'):
            data['error']['fields'] = {
                key: str(value) for key, value in exc.detail.items()
            }
        
        response.data = data
        response.status_code = response.status_code
        return response
    
    # Handle custom exceptions
    if isinstance(exc, YaWalletException):
        return Response(
            {
                'success': False,
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                    'status_code': exc.status_code
                }
            },
            status=exc.status_code
        )
    
    # Handle validation errors
    if isinstance(exc, ValidationError):
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(exc),
                    'status_code': status.HTTP_400_BAD_REQUEST
                }
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle any other exception - log it and return generic error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return Response(
        {
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An unexpected error occurred',
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
