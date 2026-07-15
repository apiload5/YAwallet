from cryptography.fernet import Fernet
from django.conf import settings
from typing import Optional
import base64

class EncryptionManager:
    """Manager for handling encryption/decryption of sensitive data"""
    
    def __init__(self):
        self.key = settings.ENCRYPTION_KEY
        self.cipher = Fernet(self.key.encode() if isinstance(self.key, str) else self.key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_data:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
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
encryption_manager = EncryptionManager()
