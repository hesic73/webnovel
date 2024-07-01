from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class Chapter(Base):
    __tablename__ = 'chapters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    novel_id = Column(Integer, ForeignKey('novels.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String)
    content = Column(Text, nullable=False)
    novel = relationship('Novel', back_populates='chapters')

    __table_args__ = (
        # Ensure chapter_number is unique within a novel
        UniqueConstraint('novel_id', 'chapter_number',
                         name='_novel_chapter_uc'),
    )
