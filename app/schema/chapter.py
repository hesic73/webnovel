from pydantic import BaseModel


class Chapter(BaseModel):
    id: int
    novel_id: int
    title: str
    content: str | None = None
