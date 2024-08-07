from sqlalchemy import Column, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import relationship

from ..base import Base

from app.enums import Genre


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
    reading_entries = relationship(
        'ReadingEntry', back_populates='novel')  # One-to-many relationship

    def __repr__(self):
        return f"{self.title}"
