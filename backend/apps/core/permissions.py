from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class IsKYCVerified(BasePermission):
    """Permission to check if user's KYC is verified"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.kyc_status != 'APPROVED':
            raise PermissionDenied('KYC verification required')
        
        return True

class IsWalletActive(BasePermission):
    """Permission to check if wallet is active and not frozen"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        wallet = request.user.wallet
        if wallet.is_frozen:
            raise PermissionDenied('Wallet is frozen')
        
        return True

class IsNotBlocked(BasePermission):
    """Permission to check if user is not blocked"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_blocked:
            raise PermissionDenied('User is blocked')
        
        return True

class HasTransactionPin(BasePermission):
    """Permission to check if user has set transaction PIN"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if not request.user.transaction_pin:
            raise PermissionDenied('Transaction PIN not set')
        
        return True
