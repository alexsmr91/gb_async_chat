import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import Column, Integer, String, Date, func
from database.dbcore import Base


class Clients(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    password_hash = Column(String)
    salt = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date, server_default=func.current_date())
    status = Column(String)

    def set_password(self, password: str) -> None:
        salt = os.urandom(16)
        password_bytes = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        password_hash = kdf.derive(password_bytes)
        self.salt = salt.hex()
        self.password_hash = password_hash.hex()

    def check_password(self, password: str) -> bool:
        salt = bytes.fromhex(self.salt)
        password_bytes = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        password_hash = kdf.derive(password_bytes)
        return password_hash.hex() == self.password_hash

    def get_dict(self):
        res = {
            'client_id': self.id,
            'login': self.login,
            'name': self.name,
            'surname': self.surname,
            'birthday_date': str(self.birthday_date),
            'status': self.status
        }
        return res

    def __repr__(self):
        return f'{self.login}'
