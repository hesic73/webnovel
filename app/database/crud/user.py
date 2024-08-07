from ..models import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.enums import UserType


def create_user(db: Session, username: str, hashed_password: str, email: str, user_type: UserType = UserType.COMMON):
    try:
        db_user = User(username=username, hashed_password=hashed_password,
                       email=email, user_type=user_type)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None


def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()
