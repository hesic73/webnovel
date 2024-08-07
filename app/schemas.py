from pydantic import BaseModel

from app.enums import Genre, UserType


class Author(BaseModel):
    id: int
    name: str


class Chapter(BaseModel):
    id: int
    novel_id: int
    title: str
    content: str | None = None


class User(BaseModel):
    id: int
    username: str
    email: str
    user_type: UserType


class Novel(BaseModel):
    id: int
    title: str
    author: Author
    genre: Genre
    description: str | None


class ReadingEntry(BaseModel):
    id: int
    novel_id: int
    title: str
    author: Author
    bookmarked_chapter: Chapter | None
    latest_chapter: Chapter | None


class AuthorNovelEntry(BaseModel):
    novel: Novel
    latest_chapter: Chapter | None