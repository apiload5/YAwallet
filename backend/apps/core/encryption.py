"""
Encryption utilities for YaWallet
"""

from cryptography.fernet import Fernet
from django.conf import settings
from typing import Optional
import base64
import logging
import os

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manager for handling encryption/decryption of sensitive data"""
    
    def __init__(self):
        # Try to get encryption key from settings or environment
        self.key = None
        
        # Try from Django settings
        try:
            self.key = getattr(settings, 'ENCRYPTION_KEY', None)
        except:
            pass
        
        # If not in settings, try environment variable
        if not self.key:
            self.key = os.environ.get('ENCRYPTION_KEY', None)
        
        # If still no key, generate one (for development only)
        if not self.key:
            logger.warning("ENCRYPTION_KEY not found. Generating temporary key for development.")
            self.key = Fernet.generate_key().decode()
        
        # Initialize cipher
        try:
            self.cipher = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {str(e)}")
            # Generate new key as fallback
            self.key = Fernet.generate_key().decode()
            self.cipher = Fernet(self.key.encode())
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        try:
            return self.cipher.encrypt(data.encode()).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            return data
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        try:
            return self.cipher.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            return encrypted_data
    
    def encrypt_dict(self, data: dict, fields: list) -> dict:
        """Encrypt specific fields in a dictionary"""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        return result
    
    def decrypt_dict(self, data: dict, fields: list) -> dict:
        """Decrypt specific fields in a dictionary"""
        result = data.copy()
        for field in fields:
            if field in result and result[field]:
                try:
                    result[field] = self.decrypt(str(result[field]))
                except:
                    pass
        return result


# Singleton instance
try:
    encryption_manager = EncryptionManager()
except Exception as e:
    logger.error(f"Failed to initialize encryption manager: {str(e)}")
    encryption_manager = None
