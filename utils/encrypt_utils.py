from cryptography.fernet import Fernet
from utils.key import get_encryption_key

fernet = Fernet(get_encryption_key())

def encrypt(data: str) -> str:
    if not data:
        return ""
    try:
        return fernet.encrypt(data.encode()).decode()
    except Exception as e:
        print("Encryption error:", e)
        return ""

def decrypt(token: str) -> str:
    try:
        return fernet.decrypt(token.encode()).decode()
    except Exception as e:
        print("Decryption error:", e)
        return ""
