from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.sql import func
from src.database.connect_db import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserModel(Base):
    __tablename__ = "users_table"

    id = Column(String, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Convert timestamp to IST (UTC+5:30)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


    def hash_password(password: str):
        return pwd_context.hash(password)
    
    def verify_password(plain_password:str, hashed_password:str):
        return pwd_context.verify(plain_password, hashed_password)
