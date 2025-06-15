import password_handler as handler
import constants
import json
from cryptography.hazmat.primitives import kdf
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode, urlsafe_b64decode
import os

DATA_FILE = 'data.json.enc'

# Global variable to store the master password for the session
master_pwd_session = None

def get_master_password() -> str:
    global master_pwd_session
    if master_pwd_session is None:
        master_pwd_session = input("Enter your master password to decrypt/encrypt data: ")
    return master_pwd_session

#TODO: revisar esta función, no se si es correcta
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # AES-256 key
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(master_password.encode('utf-8'))

