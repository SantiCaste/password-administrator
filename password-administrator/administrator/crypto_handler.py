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

def get_master_password() -> str:
    global master_pwd_session
    if master_pwd_session is None:
        master_pwd_session = input("Enter your master password to decrypt/encrypt data: ")
    return master_pwd_session

#TODO: revisar esta función, no se si es correcta
def derive_key(master_password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # 256 bits, 32 bytes lenght output
        salt=salt,
        iterations=100000, # Makes the process intentionally slow to prevent brute-force attacks
        backend=default_backend()
    )
    return kdf.derive(master_password.encode('utf-8'))

#TODO: revisar esta función, no se si es correcta
def load_registers(master_password: str) -> dict:
    if not os.path.exists(DATA_FILE):
        print("No encrypted data file found. Starting with an empty register.")
        return {}

    try:
        with open(DATA_FILE, 'rb') as f:
            encrypted_data_b64 = f.read()

        # Extract salt, nonce, and ciphertext
        encrypted_data = urlsafe_b64decode(encrypted_data_b64)
        salt = encrypted_data[:SALT_LENGTH]
        nonce = encrypted_data[SALT_LENGTH:SALT_LENGTH + NONCE_LENGTH]
        tag = encrypted_data[-TAG_LENGTH:]
        ciphertext = encrypted_data[SALT_LENGTH + NONCE_LENGTH:-TAG_LENGTH]

        key = derive_key(master_password, salt)
        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        registers = json.loads(decrypted_data.decode('utf-8'))
        print("Registers loaded and decrypted successfully.")
    except Exception as e:
        # handle InvalidTag exception:
        if isinstance(e, InvalidTag):
            print("Decryption failed: Invalid tag. The data may be corrupted or the master password is incorrect.")
        else:
            # Handle exceptions such as file not found, decryption errors, etc.
            #TODO: manejar la excepción de otra manera, podemos pedir al usuario que vuelva a introducir la contraseña maestra
            print(f"Error loading or decrypting data: {e}")
        # TODO: definir qué vamos a hacer si falla la desencriptación
        #registers = {} # Clear registers if decryption fails
        # Optionally, you might want to ask the user to re-enter master password
        # or handle this error more gracefully, e.g., by exiting.
        exit(1)
    return registers

def save_registers(registers: dict, master_password: str):
    try:
        salt = os.urandom(SALT_LENGTH)
        key = derive_key(master_password, salt)
        nonce = os.urandom(NONCE_LENGTH) # Nonce for GCM

        cipher = Cipher(algorithms.AES(key), modes.GCM(nonce), backend=default_backend())
        encryptor = cipher.encryptor()
        json_data = json.dumps(registers).encode('utf-8')
        ciphertext = encryptor.update(json_data) + encryptor.finalize()

        # Combine salt, nonce, and ciphertext for storage
        encrypted_data = salt + nonce + ciphertext + encryptor.tag
        with open(DATA_FILE, 'wb') as f:
            f.write(urlsafe_b64encode(encrypted_data))
        print("Registers encrypted and saved successfully.")
    except Exception as e:
        #TODO: manejar la excepción de otra manera quizá
        print(f"Error saving or encrypting data: {e}")