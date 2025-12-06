"""
ARIN Platform - Data Encryption
Шифрование данных at rest и in transit
"""
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os

from backend.config import settings

logger = logging.getLogger(__name__)


class DataEncryption:
    """
    Шифрование данных
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Инициализация Data Encryption
        
        Args:
            key: Ключ шифрования (если None, генерируется из SECRET_KEY)
        """
        if key:
            self.key = key
        else:
            # Генерация ключа из SECRET_KEY
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'arin_platform_salt',  # В production использовать случайную соль
                iterations=100000,
                backend=default_backend()
            )
            secret_key_bytes = settings.secret_key.encode()
            self.key = base64.urlsafe_b64encode(kdf.derive(secret_key_bytes))
        
        self.cipher = Fernet(self.key)
        
    @staticmethod
    def generate_key() -> bytes:
        """
        Генерация нового ключа шифрования
        
        Returns:
            Ключ в формате bytes
        """
        return Fernet.generate_key()
        
    def encrypt(self, data: str) -> str:
        """
        Шифрование данных
        
        Args:
            data: Данные для шифрования
            
        Returns:
            Зашифрованные данные (base64)
        """
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
            
    def decrypt(self, encrypted_data: str) -> str:
        """
        Расшифровка данных
        
        Args:
            encrypted_data: Зашифрованные данные (base64)
            
        Returns:
            Расшифрованные данные
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


# Глобальный экземпляр
data_encryption = DataEncryption()

