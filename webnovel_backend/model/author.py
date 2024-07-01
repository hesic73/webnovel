from pydantic import BaseModel

class AuthorCreate(BaseModel):
    name: str

class Author(BaseModel):
    id: int
    name: str
