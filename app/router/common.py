from fastapi import APIRouter, HTTPException

from app.schema.reading_entry import ReadingEntryCreate, ReadingEntryDelete, ReadingEntryUpdate, ReadingEntry
from app.database import DBDependency
from app import database


router = APIRouter()


@router.post("/reading-entries/", response_model=ReadingEntry)
def create_reading_entry(entry: ReadingEntryCreate, db: DBDependency):
    db_entry = database.get_reading_entry(
        db, user_id=entry.user_id, novel_id=entry.novel_id)
    if db_entry:
        raise HTTPException(
            status_code=409, detail="Reading entry already exists")
    return database.create_reading_entry(db=db, user_id=entry.user_id, novel_id=entry.novel_id, current_chapter_id=entry.current_chapter_id)


@router.delete("/reading-entries/", response_model=dict)
def delete_reading_entry(entry: ReadingEntryDelete, db: DBDependency):
    db_entry = database.get_reading_entry(
        db, user_id=entry.user_id, novel_id=entry.novel_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Reading entry not found")
    database.delete_reading_entry(db=db, entry=db_entry)
    return {"message": "Reading entry removed successfully"}


@router.put("/reading-entries/progress", response_model=ReadingEntry)
def update_reading_progress(entry: ReadingEntryUpdate, db: DBDependency):
    db_entry = database.get_reading_entry(
        db, user_id=entry.user_id, novel_id=entry.novel_id)
    if not db_entry:
        raise HTTPException(status_code=404, detail="Reading entry not found")
    return database.update_reading_progress(db=db, user_id=entry.user_id, novel_id=entry.novel_id, chapter_id=entry.current_chapter_id)
