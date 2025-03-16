import os
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

class PasswordManager:
    def __init__(self):
        self.ph = PasswordHasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=4,
            hash_len=32,
            salt_len=16,
            encoding='utf-8'
        )
    
    def hash_password(self, password):
        return self.ph.hash(password)
    
    def verify_password(self, hash, password):
        try:
            return self.ph.verify(hash, password)
        except VerifyMismatchError:
            return False
        
    def check_needs_rehash(self, hash):
        return self.ph.check_needs_rehash(hash)
