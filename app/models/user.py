from sqlalchemy import Column, String
from .base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
