from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Session
from .base import Base


class ReadingEntry(Base):
    __tablename__ = 'reading_entries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'),
                     nullable=False)  # Foreign key to User table
    novel_id = Column(Integer, ForeignKey('novels.id'),
                      nullable=False)  # Foreign key to Novel table
    current_chapter_id = Column(Integer, ForeignKey(
        'chapters.id'), nullable=True)  # Foreign key to Chapter table

    # Back-populate to User model
    user = relationship('User', back_populates='reading_entries')
    # Back-populate to Novel model
    novel = relationship('Novel', back_populates='reading_entries')
    current_chapter = relationship('Chapter')  # Relationship to Chapter model

    __table_args__ = (
        # Ensure unique novel per user
        UniqueConstraint('user_id', 'novel_id', name='_user_novel_uc'),
    )

    def __repr__(self):
        return f"User {self.user_id} reading {self.novel_id}, currently at chapter {self.current_chapter_id}"


def create_reading_entry(db: Session, user_id: int, novel_id: int, current_chapter_id: int | None = None):
    reading_entry = ReadingEntry(
        user_id=user_id, novel_id=novel_id, current_chapter_id=current_chapter_id)
    db.add(reading_entry)
    db.commit()
    db.refresh(reading_entry)
    return reading_entry


def update_reading_progress(db: Session, user_id: int, novel_id: int, chapter_id: int):
    reading_entry = db.query(ReadingEntry).filter_by(
        user_id=user_id, novel_id=novel_id).first()
    if reading_entry:
        reading_entry.current_chapter_id = chapter_id
        db.commit()
        db.refresh(reading_entry)
    return reading_entry


def get_user_reading_entries(db: Session, user_id: int):
    return db.query(ReadingEntry).filter_by(user_id=user_id).all()


def get_reading_entry(db: Session, user_id: int, novel_id: int):
    return db.query(ReadingEntry).filter_by(user_id=user_id, novel_id=novel_id).first()


def remove_novel_from_reading_entry(db: Session, user_id: int, novel_id: int):
    reading_entry = db.query(ReadingEntry).filter_by(
        user_id=user_id, novel_id=novel_id).first()
    if reading_entry:
        db.delete(reading_entry)
        db.commit()
    return reading_entry
