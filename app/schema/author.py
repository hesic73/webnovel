from pydantic import BaseModel


class Author(BaseModel):
    id: int
    name: str
