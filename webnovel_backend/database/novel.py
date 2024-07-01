from sqlalchemy import Column, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session

from .base import Base
from .author import find_or_create_author_id

from webnovel_backend.enums import Genre


class Novel(Base):
    __tablename__ = 'novels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False, unique=True)
    author_id = Column(Integer, ForeignKey('authors.id'), nullable=False)
    genre = Column(Enum(Genre), nullable=False)
    description = Column(Text)
    author = relationship('Author', back_populates='novels')
    chapters = relationship(
        'Chapter', back_populates='novel', cascade='all, delete-orphan')


def create_novel(db: Session, title: str, author_name: str, genre: Genre, description: str = None):
    author_id = find_or_create_author_id(db, author_name)
    db_novel = Novel(
        title=title,
        author_id=author_id,
        genre=genre,
        description=description
    )
    db.add(db_novel)
    db.commit()
    db.refresh(db_novel)
    return db_novel


def get_novels(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Novel).offset(skip).limit(limit).all()


def get_novel(db: Session, novel_id: int):
    return db.query(Novel).filter(Novel.id == novel_id).first()


def update_novel(db: Session, novel_id: int, title: str = None, author_name: str = None, genre: Genre = None, description: str = None):
    db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not db_novel:
        return None

    if title:
        db_novel.title = title

    if author_name:
        author_id = find_or_create_author_id(db, author_name)
        db_novel.author_id = author_id

    if genre:
        db_novel.genre = genre

    if description:
        db_novel.description = description

    db.commit()
    db.refresh(db_novel)
    return db_novel


def delete_novel(db: Session, novel_id: int):
    db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not db_novel:
        return None

    db.delete(db_novel)
    db.commit()
    return db_novel
