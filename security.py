from bcrypt import hashpw, gensalt, checkpw

from secrets import token_urlsafe

from hashlib import sha256
from base64 import urlsafe_b64encode

from cryptography.fernet import Fernet

from time import time

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("ENCRYPTION_KEY")

class Security:
    def __init__(self):
        key_bytes = SECRET_KEY.encode("utf-8")
        key_digest = sha256(key_bytes).digest()
        fernet_key = urlsafe_b64encode(key_digest)
        self._fernet = Fernet(fernet_key)


    def hash_password(self, password: str) -> str:
        return hashpw(password.encode("utf-8"), gensalt()).decode("utf-8")
    
    def check_password(self, password: str, hashed_password: str) -> bool:
        return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    
    def encrypt(self, secret_data: str) -> str:
        return self._fernet.encrypt(secret_data.encode("utf-8")).decode("utf-8")
    
    def decrypt(self, encrtpted_data: str) -> str:
        return self._fernet.decrypt(encrtpted_data.encode("utf-8")).decode("utf-8")
    
    def create_secret_key(self) -> str:
        return token_urlsafe(32)
    
    
security_instanse = Security()


