from sqlalchemy.orm import validates
from sqlalchemy import Column, Integer, String
from hashlib import sha256

from messenger.core.models import Base
from messenger.api import validators


class User(Base):
    __tablename__: str = "user"

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    username: Column = Column(String, unique=True)
    pwd_hash: Column = Column(String(64))
    email: Column = Column(String)

    def __repr__(self) -> str:
        return f"<User(username={self.username}, pwd_hash={self.pwd_hash}, email={self.email})>"

    def verify_password(self, password: str) -> bool:
        return sha256(password.encode("utf-8")).hexdigest() == self.pwd_hash

    @validates("username")
    def validate_username(self, _, username: str) -> str:
        if not validators.validate_username(username):
            raise ValueError("Incorrect username format.")
        return username

    @validates("email")
    def validate_email(self, _, email: str) -> str:
        if not validators.validate_email(email):
            raise ValueError("Incorrect email format.")
        return email

    @validates("pwd_hash")
    def validate_password_hash(self, _, pwd_hash: str) -> str:
        if not validators.validate_password_sha256_hash(pwd_hash):
            raise ValueError("Incorrect password format.")
        return pwd_hash
