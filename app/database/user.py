from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

from .base import Base

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


def create_user(db: Session, username: str, hashed_password: str, email: str, user_type: UserType = UserType.COMMON):
    db_user = User(username=username, hashed_password=hashed_password,
                   email=email, user_type=user_type)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
