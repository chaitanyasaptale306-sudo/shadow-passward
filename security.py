import time
import jwt
import hashlib
from cryptography.fernet import Fernet
import os

# Secret key management
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-cyberpunk-shadow-key-3000")
DATA_ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(DATA_ENCRYPTION_KEY)

def encrypt_embedding(embedding_data: str) -> str:
    """Encrypts raw biometric embedding string into Fernet ciphertext."""
    return cipher_suite.encrypt(embedding_data.encode()).decode()

def decrypt_embedding(token: str) -> str:
    """Decrypts Fernet ciphertext back to raw embedding string."""
    return cipher_suite.decrypt(token.encode()).decode()

def generate_jwt(user_id: int, username: str) -> str:
    """Generates a secure 1-hour session JWT token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": time.time() + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_jwt(token: str):
    """Verifies JWT signature and expiration."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except Exception:
        return None