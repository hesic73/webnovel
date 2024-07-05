from pydantic import BaseModel

from app.enums import Genre


class NovelCreate(BaseModel):
    title: str
    author_name: str
    genre: Genre
    description: str | None = None


class Novel(BaseModel):
    title: str
    id: int
    author_name: str
    author_id: int
    genre: Genre
    description: str | None = None
