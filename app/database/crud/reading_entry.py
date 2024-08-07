from sqlalchemy.orm import Session
from ..models import ReadingEntry


def create_reading_entry(db: Session, user_id: int, novel_id: int, current_chapter_id: int | None = None):
    reading_entry = ReadingEntry(
        user_id=user_id, novel_id=novel_id, current_chapter_id=current_chapter_id)
    db.add(reading_entry)
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


def count_user_reading_entries(db: Session, user_id: int):
    return db.query(ReadingEntry).filter_by(user_id=user_id).count()
