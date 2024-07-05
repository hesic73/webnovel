from pydantic import BaseModel


class ReadingEntryBase(BaseModel):
    user_id: int
    novel_id: int


class ReadingEntryCreate(ReadingEntryBase):
    current_chapter_id: int | None = None


class ReadingEntryUpdate(ReadingEntryBase):
    current_chapter_id: int


class ReadingEntryDelete(ReadingEntryBase):
    pass


class ReadingEntry(ReadingEntryBase):
    id: int
    current_chapter_id: int | None = None
