import os
from cryptography.fernet import Fernet

def get_encryption_key():
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError("ENCRYPTION_KEY not found in environment variables")
    return key
