from pydantic import BaseModel

from app.enums import Genre


class Novel(BaseModel):
    id: int
    title: str
    author_name: str
    genre: Genre
    description: str


class NovelUpdate(BaseModel):
    id: int
    title: str | None = None
    author_name: str | None = None
    genre: Genre | None = None
    description: str | None = None
