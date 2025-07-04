import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidTag
from base64 import urlsafe_b64encode, urlsafe_b64decode
import os

DATA_FILE = 'data.json.enc'
SALT_LENGTH = 16 # 128 bits, 1 block of AES
NONCE_LENGTH = 16
TAG_LENGTH = 16

# Global variable to store the master password for the session
master_pwd_session = None

def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 256 bits, 32 bytes lenght output
        salt=salt,
        iterations=100000, # Makes the process intentionally slow to prevent brute-force attacks
        backend=default_backend()
    )
    return kdf.derive(master_password.encode('utf-8'))

# Modified to return status
def load_registers(master_password: str, path: str) -> tuple[dict | None, str]: # Returns (registers, status_message)
    if not os.path.exists(path):
        return None, "FILE_NOT_FOUND"

    try:
        with open(path, 'rb') as f:
            encrypted_data_b64 = f.read()

        encrypted_data = urlsafe_b64decode(encrypted_data_b64)
        salt = encrypted_data[:SALT_LENGTH]
        nonce = encrypted_data[SALT_LENGTH:SALT_LENGTH + NONCE_LENGTH]
        tag = encrypted_data[-TAG_LENGTH:]
        ciphertext = encrypted_data[32:-16]

        key = derive_key(master_password, salt)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        registers = json.loads(decrypted_data.decode('utf-8'))
        return registers, "SUCCESS"
    except InvalidTag:
        return None, "INVALID_PASSWORD"
    except Exception as e:
        return None, f"DECRYPTION_ERROR: {e}"

def save_registers(registers: dict, master_password: str, path: str):
    try:
        salt = os.urandom(SALT_LENGTH)
        key = derive_key(master_password, salt)
        nonce = os.urandom(16)

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        json_data = json.dumps(registers).encode('utf-8')
        ciphertext = encryptor.update(json_data) + encryptor.finalize()

        encrypted_data = salt + nonce + ciphertext + encryptor.tag
        with open(path, 'wb') as f:
            f.write(urlsafe_b64encode(encrypted_data))
        # print("Registers encrypted and saved successfully.")
    except FileExistsError:
        # print(f"File '{path}' already exists")
        raise FileExistsError(f"File '{path}' already exists")
    except Exception as e:
        # print(f"Error saving or encrypting data: {e}")

def create_empty_registers(master_password: str, path: str):
    """Creates a new, empty encrypted data file."""
    # This will overwrite an existing file if it has the same name
    save_registers({}, master_password, path)