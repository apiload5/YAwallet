"""
Constants used across the YaWallet application
"""

from django.db import models

# KYC Status Choices
KYC_STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
]

# Device Types
DEVICE_TYPES = [
    ('ANDROID', 'Android'),
    ('IOS', 'iOS'),
    ('WEB', 'Web'),
    ('OTHER', 'Other'),
]

# Transaction Types
TRANSACTION_TYPES = [
    ('ADD_MONEY', 'Add Money'),
    ('P2P_TRANSFER', 'P2P Transfer'),
    ('BANK_TRANSFER', 'Bank Transfer'),
    ('QR_PAYMENT', 'QR Payment'),
    ('BILL_PAYMENT', 'Bill Payment'),
    ('WITHDRAWAL', 'Withdrawal'),
    ('REFUND', 'Refund'),
    ('FEE', 'Fee'),
]

# Transaction Status
TRANSACTION_STATUS = [
    ('PENDING', 'Pending'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
    ('CANCELLED', 'Cancelled'),
    ('REFUNDED', 'Refunded'),
]

# Payment Methods
PAYMENT_METHODS = [
    ('CARD', 'Card'),
    ('BANK', 'Bank'),
    ('EASYPAISA', 'Easypaisa'),
    ('JAZZCASH', 'JazzCash'),
    ('NIFT', 'NIFT'),
    ('WALLET', 'Wallet'),
]

# Bill Categories
BILL_CATEGORIES = [
    ('ELECTRICITY', 'Electricity'),
    ('GAS', 'Gas'),
    ('INTERNET', 'Internet'),
    ('WATER', 'Water'),
    ('TELEPHONE', 'Telephone'),
    ('EDUCATION', 'Education'),
    ('OTHER', 'Other'),
]

# User Roles
USER_ROLES = [
    ('USER', 'User'),
    ('ADMIN', 'Admin'),
    ('SUPPORT', 'Support'),
    ('MERCHANT', 'Merchant'),
]

# Notification Types
NOTIFICATION_TYPES = [
    ('TRANSFER', 'Transfer'),
    ('PAYMENT', 'Payment'),
    ('KYC', 'KYC'),
    ('SECURITY', 'Security'),
    ('PROMOTIONAL', 'Promotional'),
]

# Audit Actions
AUDIT_ACTIONS = [
    ('USER_REGISTERED', 'User Registered'),
    ('USER_LOGIN', 'User Login'),
    ('USER_LOGOUT', 'User Logout'),
    ('KYC_SUBMITTED', 'KYC Submitted'),
    ('KYC_VERIFIED', 'KYC Verified'),
    ('KYC_REJECTED', 'KYC Rejected'),
    ('ADD_MONEY', 'Add Money'),
    ('P2P_TRANSFER', 'P2P Transfer'),
    ('QR_PAYMENT', 'QR Payment'),
    ('BILL_PAYMENT', 'Bill Payment'),
    ('WITHDRAWAL', 'Withdrawal'),
    ('TRANSACTION_PIN_SET', 'Transaction PIN Set'),
    ('TRANSACTION_PIN_VERIFIED', 'Transaction PIN Verified'),
    ('WALLET_FROZEN', 'Wallet Frozen'),
    ('WALLET_UNFROZEN', 'Wallet Unfrozen'),
    ('USER_BLOCKED', 'User Blocked'),
    ('USER_UNBLOCKED', 'User Unblocked'),
]

# Error Codes
ERROR_CODES = {
    'INSUFFICIENT_BALANCE': 'Insufficient balance',
    'INVALID_PIN': 'Invalid PIN',
    'KYC_REQUIRED': 'KYC verification required',
    'WALLET_FROZEN': 'Wallet is frozen',
    'USER_BLOCKED': 'User is blocked',
    'DEVICE_LIMIT_EXCEEDED': 'Device limit exceeded',
    'INVALID_TRANSACTION': 'Invalid transaction',
    'DUPLICATE_TRANSACTION': 'Duplicate transaction',
    'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded',
    'INVALID_QR': 'Invalid QR code',
    'BILLER_NOT_FOUND': 'Biller not found',
    'PAYMENT_FAILED': 'Payment failed',
    'INVALID_IBFT': 'Invalid IBFT transfer',
}
