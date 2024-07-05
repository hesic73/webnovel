from pydantic import BaseModel


class ReadingEntryDisplay(BaseModel):
    id: int  # for deletion 需要检权，用户只能删除自己的
    novel_id: int
    title: str
    author: str
    chapter_id: int | None
    chapter_name: str | None


class ReadingEntryDelete(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None

class ReadingEntryUpdate(BaseModel):
    user_id: int
    novel_id: int
    current_chapter_id: int | None = None
