from cryptography.fernet import Fernet
import os

# Load Fernet key from environment
SECRET_KEY = os.getenv("SECRET_KEY")
cipher = Fernet(SECRET_KEY.encode())

def encrypt_password(password: str) -> str:
    """Encrypt a password string"""
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(token: str) -> str:
    """Decrypt a password string"""
    return cipher.decrypt(token.encode()).decode()