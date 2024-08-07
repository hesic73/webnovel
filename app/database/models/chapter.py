from sqlalchemy import Column, Integer, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Session
from sqlalchemy.exc import SQLAlchemyError

from ..base import Base


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

    def __repr__(self):
        return f"{self.chapter_number} {self.title}"


def create_chapter(db: Session, novel_id: int, chapter_number: int, title: str, content: str):
    db_chapter = Chapter(
        novel_id=novel_id,
        chapter_number=chapter_number,
        title=title,
        content=content
    )
    try:
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Error creating chapter: {e}")
        return None


def get_chapters(db: Session, novel_id: int, skip: int = 0, limit: int = 10):
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number).offset(skip).limit(limit).all()


def get_all_chapters(db: Session, novel_id: int):
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number).all()


def get_chapters_reversed(db: Session, novel_id: int, skip: int = 0, limit: int = 10):
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number.desc()).offset(skip).limit(limit).all()


def get_total_chapters_count(db: Session, novel_id: int) -> int:
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).count()


def get_chapter(db: Session, chapter_id: int):
    return db.query(Chapter).filter(Chapter.id == chapter_id).first()


def update_chapter(db: Session, chapter_id: int, title: str = None, content: str = None):
    db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    if not db_chapter:
        return None

    if title:
        db_chapter.title = title

    if content:
        db_chapter.content = content

    db.commit()
    db.refresh(db_chapter)
    return db_chapter


def get_previous_chapter(db: Session, novel_id: int, chapter_number: int):
    return db.query(Chapter).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_number < chapter_number
    ).order_by(Chapter.chapter_number.desc()).first()


def get_next_chapter(db: Session, novel_id: int, chapter_number: int):
    return db.query(Chapter).filter(
        Chapter.novel_id == novel_id,
        Chapter.chapter_number > chapter_number
    ).order_by(Chapter.chapter_number.asc()).first()


def get_first_chapter(db: Session, novel_id: int):
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number.asc()).first()


def get_last_chapter(db: Session, novel_id: int):
    return db.query(Chapter).filter(Chapter.novel_id == novel_id).order_by(Chapter.chapter_number.desc()).first()
