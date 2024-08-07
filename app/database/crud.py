from .models import *


# User CRUD

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


def create_author(db: Session, name: str):
    db_author = Author(name=name)
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    return db_author


# Author CRUD

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


# Chapter CRUD


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


# Novel CRUD


def create_novel(db: Session, title: str, author_name: str, genre: Genre, description: str = None):
    author_id = find_or_create_author_id(db, author_name)
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


def get_novel_with_chapters(db: Session, novel_id: int):
    return db.query(Novel).filter(Novel.id == novel_id).options(joinedload(Novel.chapters)).first()


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


# Reading Entry CRUD

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
