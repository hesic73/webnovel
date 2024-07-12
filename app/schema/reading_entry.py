from pydantic import BaseModel
from .author import Author
from .chapter import Chapter


class ReadingEntryDisplay(BaseModel):
    id: int  # for deletion 需要检权，用户只能删除自己的
    novel_id: int
    title: str
    author: Author
    bookmarked_chapter: Chapter | None
    latest_chapter: Chapter | None


class ReadingEntryDelete(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None


class ReadingEntryUpdate(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None
