from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import os

def get_key(password_provided):
    password = password_provided.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"salt", #This has to always be the same to get the same value for the same password
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key
    
def encrypt(text,key):
    message = text.encode("utf-8")
    f = Fernet(key)
    encrypted = f.encrypt(message)
    return encrypted

def decrypt(encrypted,key):
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)
    return decrypted.decode("utf-8")
