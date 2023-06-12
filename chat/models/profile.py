from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from sqlalchemy import Column, Integer, String, Date, func
from database.dbcore import Base
from config import SALT


class Profile(Base):
    __tablename__ = 'profile'

    client_id = Column(Integer, primary_key=True)
    login = Column(String)
    password_hash = Column(String)
    name = Column(String)
    surname = Column(String)
    birthday_date = Column(Date, server_default=func.current_date())
    status = Column(String)

    def set_password(self, password):
        password_bytes = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
        )
        password_hash = kdf.derive(password_bytes)
        self.password_hash = password_hash.hex()

    def check_password(self, password):
        password_bytes = password.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=SALT,
            iterations=100000,
        )
        password_hash = kdf.derive(password_bytes)
        return password_hash.hex() == self.password_hash

    def __repr__(self):
        return f'{self.login}'
