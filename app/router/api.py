from fastapi import APIRouter, HTTPException

from pydantic import BaseModel

from app.schema.reading_entry import ReadingEntryDisplay, ReadingEntryDelete, ReadingEntryUpdate
from app.schema.novel import Novel
from app.database import DBDependency
from app import database

from app.securities import TokenPayloadDependency

from app.enums import Genre


BOOKSHELF_SIZE = 10


router = APIRouter()


class BookshelfInfo(BaseModel):
    username: str
    entries: list[ReadingEntryDisplay]


@router.get("/bookshelf/", response_model=BookshelfInfo)
async def get_bookshelf(db: DBDependency, payload: TokenPayloadDependency):
    username = payload.sub

    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user.id

    # Query the reading entries
    reading_entries = database.get_user_reading_entries(db=db, user_id=user_id)

    # Prepare the response data
    entries = []
    for entry in reading_entries:
        e = {
            "id": entry.id,
            "novel_id": entry.novel_id,
            "title": entry.novel.title,
            "author": {
                "id": entry.novel.author.id,
                "name": entry.novel.author.name
            },
            "chapter_id": entry.current_chapter.id if entry.current_chapter else None,
            "chapter_name": entry.current_chapter.title if entry.current_chapter else None
        }
        entries.append(e)

    return BookshelfInfo(username=username, entries=entries)


@router.delete("/bookshelf/{novel_id}/", response_model=ReadingEntryDelete)
async def remove_novel_from_bookshelf(db: DBDependency, payload: TokenPayloadDependency, novel_id: int):
    username = payload.sub

    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Remove the novel from the reading entries
    entry = database.remove_novel_from_reading_entry(
        db=db, user_id=user.id, novel_id=novel_id)

    return entry


class BookmarkRequest(BaseModel):
    novel_id: int
    chapter_id: int | None = None


@router.post("/bookmark/", response_model=ReadingEntryUpdate)
async def add_bookmark(bookmark: BookmarkRequest, db: DBDependency, payload: TokenPayloadDependency):
    username = payload.sub

    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

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


@router.put("/novel/{novel_id}/", response_model=Novel)
async def update_novel(novel: NovelUpdate, db: DBDependency):
    db_novel = database.update_novel(db=db, novel_id=novel.id, title=novel.title,
                                     author_name=novel.author_name, genre=novel.genre, description=novel.description)
    if not db_novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return db_novel
