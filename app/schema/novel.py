from pydantic import BaseModel

from app.enums import Genre

from .author import Author


class Novel(BaseModel):
    id: int
    title: str
    author: Author
    genre: Genre
    description: str | None
