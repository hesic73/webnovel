from ..models import Novel
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from app.enums import Genre


def create_novel(db: Session,
                 title: str,
                 author_id: int,
                 genre: Genre,
                 description: str | None = None):
    try:
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
    except Exception as e:
        db.rollback()
        print(f"Error creating novel: {e}")
        return None


def get_total_novels_count(db: Session):
    return db.query(Novel).count()


def get_novels(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Novel).offset(skip).limit(limit).all()


def get_novel(db: Session, novel_id: int):
    return db.query(Novel).filter(Novel.id == novel_id).first()


def get_novel_with_author(db: Session, novel_id: int) -> Novel:
    return db.query(Novel).filter(Novel.id == novel_id).options(joinedload(Novel.author)).first()


def get_novel_with_chapters(db: Session, novel_id: int):
    return db.query(Novel).filter(Novel.id == novel_id).options(joinedload(Novel.chapters)).first()


def update_novel(db: Session,
                 novel_id: int,
                 author_id: int | None = None,
                 title: str | None = None,
                 genre: Genre | None = None,
                 description: str | None = None):
    db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
    if not db_novel:
        return None

    if title:
        db_novel.title = title

    if author_id:
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
