from fastapi import APIRouter, HTTPException
from fastapi import status

from pydantic import BaseModel

from app import models
from app.database import DBDependency
from app import database

from app.utils.auth_utils import RequireUserDependency

from app.enums import Genre, UserType

from app.consts import BOOKSHELF_SIZE

router = APIRouter()


class BookshelfInfo(BaseModel):
    username: str
    user_type: UserType
    entries: list[models.ReadingEntry]


@router.get("/bookshelf/", response_model=BookshelfInfo)
async def get_bookshelf(db: DBDependency, user: RequireUserDependency):

    user_id = user.id
    username = user.username

    # Query the reading entries
    reading_entries = database.get_user_reading_entries(db=db, user_id=user_id)

    # Prepare the response data
    entries = []
    for entry in reading_entries:
        if entry.current_chapter:
            bookmarked_chapter = models.Chapter(
                id=entry.current_chapter.id, novel_id=entry.novel_id, title=entry.current_chapter.title)
        else:
            bookmarked_chapter = None

        if _latest_chapter := database.get_last_chapter(
                db=db, novel_id=entry.novel_id):
            latest_chapter = models.Chapter(
                id=_latest_chapter.id, novel_id=entry.novel_id, title=_latest_chapter.title)
        else:
            latest_chapter = None

        e = models.ReadingEntry(id=entry.id, novel_id=entry.novel_id, title=entry.novel.title,
                                author=models.Author(
                                    id=entry.novel.author.id, name=entry.novel.author.name),
                                bookmarked_chapter=bookmarked_chapter, latest_chapter=latest_chapter)

        entries.append(e)

    return BookshelfInfo(username=username, user_type=user.user_type, entries=entries)


class ReadingEntryDelete(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None


class ReadingEntryUpdate(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None


@router.delete("/bookshelf/{novel_id}/", response_model=ReadingEntryDelete)
async def remove_novel_from_bookshelf(db: DBDependency, user: RequireUserDependency, novel_id: int):

    # Remove the novel from the reading entries
    entry = database.remove_novel_from_reading_entry(
        db=db, user_id=user.id, novel_id=novel_id)

    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reading entry not found")

    return entry


class BookmarkRequest(BaseModel):
    novel_id: int
    chapter_id: int | None = None


@router.post("/bookmark/", response_model=ReadingEntryUpdate)
async def add_bookmark(bookmark: BookmarkRequest, db: DBDependency, user: RequireUserDependency):

    user_id = user.id

    # Check if the reading entry exists
    reading_entry = database.get_reading_entry(
        db, user_id=user_id, novel_id=bookmark.novel_id)

    if reading_entry:
        if bookmark.chapter_id:
            # Update existing reading entry
            reading_entry.current_chapter_id = bookmark.chapter_id
            db.commit()
            db.refresh(reading_entry)

        return reading_entry

    count = database.count_user_reading_entries(db=db, user_id=user_id)

    if count >= BOOKSHELF_SIZE:
        raise HTTPException(
            status_code=400, detail=f"User has reached the maximum bookshelf size of {BOOKSHELF_SIZE}")

    reading_entry = database.create_reading_entry(
        db=db,
        user_id=user_id,
        novel_id=bookmark.novel_id,
        current_chapter_id=bookmark.chapter_id
    )

    return reading_entry


# update the novel


class NovelUpdate(BaseModel):
    id: int
    title: str | None = None
    author_name: str | None = None
    genre: Genre | None = None
    description: str | None = None


@router.put("/novel/{novel_id}/", response_model=models.Novel)
async def update_novel(novel: NovelUpdate, db: DBDependency):
    db_novel = database.update_novel(db=db, novel_id=novel.id, title=novel.title,
                                     author_name=novel.author_name, genre=novel.genre, description=novel.description)
    if not db_novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return db_novel
