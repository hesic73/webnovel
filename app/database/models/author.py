from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from ..base import Base


class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    novels = relationship('Novel', back_populates='author',
                          cascade='all, delete-orphan')

    def __repr__(self):
        return f"{self.name}"
