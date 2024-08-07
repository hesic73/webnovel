from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..base import Base

from app.enums import UserType


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    user_type = Column(Enum(UserType), nullable=False)

    reading_entries = relationship(
        'ReadingEntry', back_populates='user', cascade='all, delete-orphan')  # One-to-many relationship

    def __repr__(self):
        return f"{self.username}"
