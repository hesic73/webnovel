from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from .base import Base


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    novels = relationship('Novel', back_populates='author',
                          cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name}"


def create_author(db: Session, name: str):
    db_author = Author(name=name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Author).offset(skip).limit(limit).all()


def get_author_by_name(db: Session, name: str):
    return db.query(Author).filter(Author.name == name).first()


def get_author_by_id(db: Session, author_id: int):
    return db.query(Author).filter(Author.id == author_id).first()


def get_author_with_novels(db: Session, author_id: int):
    return db.query(Author).filter(Author.id == author_id).options(joinedload(Author.novels)).first()


def find_or_create_author_id(db: Session, name: str) -> int:
    author = db.query(Author).filter(Author.name == name).first()
    if author:
        return author.id
    else:
        new_author = Author(name=name)
        db.add(new_author)
        db.commit()
        db.refresh(new_author)
        return new_author.id
