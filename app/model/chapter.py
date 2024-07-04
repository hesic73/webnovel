from pydantic import BaseModel

class Chapter(BaseModel):
    id: int
    novel_id: int
    chapter_number: int
    title: str
    content: str
