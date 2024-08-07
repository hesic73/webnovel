from fastapi import APIRouter, HTTPException
from fastapi import status

from pydantic import BaseModel

from app import schemas
from app.database.session import DBDependency
from app.database import crud

from app.utils.auth_utils import RequireUserDependency

from app.enums import UserType

from app.consts import BOOKSHELF_SIZE

router = APIRouter()


class BookshelfInfo(BaseModel):
    username: str
    user_type: UserType
    entries: list[schemas.ReadingEntry]


@router.get("/bookshelf/", response_model=BookshelfInfo)
async def get_bookshelf(db: DBDependency, user: RequireUserDependency):

    user_id = user.id
    username = user.username

    # Query the reading entries
    reading_entries = crud.get_user_reading_entries(db=db, user_id=user_id)

    last_chapters = crud.get_last_chapters(db=db, novel_ids=[
        entry.novel_id for entry in reading_entries])

    # Prepare the response data
    entries = []
    for entry, _latest_chapter in zip(reading_entries, last_chapters):
        if entry.current_chapter:
            bookmarked_chapter = schemas.Chapter(
                id=entry.current_chapter.id, novel_id=entry.novel_id, title=entry.current_chapter.title)
        else:
            bookmarked_chapter = None

        if _latest_chapter is not None:
            latest_chapter = schemas.Chapter(
                id=_latest_chapter.id, novel_id=entry.novel_id, title=_latest_chapter.title)
        else:
            latest_chapter = None

        e = schemas.ReadingEntry(id=entry.id, novel_id=entry.novel_id, title=entry.novel.title,
                                 author=schemas.Author(
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
    entry = crud.remove_novel_from_reading_entry(
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
    reading_entry = crud.get_reading_entry(
        db, user_id=user_id, novel_id=bookmark.novel_id)

    if reading_entry:
        if bookmark.chapter_id:
            # Update existing reading entry
            reading_entry.current_chapter_id = bookmark.chapter_id
            db.commit()
            db.refresh(reading_entry)

        return reading_entry

    count = crud.count_user_reading_entries(db=db, user_id=user_id)

    if count >= BOOKSHELF_SIZE:
        raise HTTPException(
            status_code=400, detail=f"User has reached the maximum bookshelf size of {BOOKSHELF_SIZE}")

    reading_entry = crud.create_reading_entry(
        db=db,
        user_id=user_id,
        novel_id=bookmark.novel_id,
        current_chapter_id=bookmark.chapter_id
    )

    return reading_entry
