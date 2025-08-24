from sqlalchemy import Boolean, Column, Integer, String, DateTime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    # username = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(255))
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)


