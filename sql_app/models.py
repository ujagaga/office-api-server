from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    token = Column(Integer, default=0)
    token_expire_time = Column(Integer, default=0)
