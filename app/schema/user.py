from pydantic import BaseModel
from app.enums import UserType


class User(BaseModel):
    id: int
    username: str
    email: str
    user_type: UserType
