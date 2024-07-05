from fastapi import APIRouter, HTTPException, status
from fastapi import Depends, HTTPException

from pydantic import BaseModel, EmailStr

from app.database import DBDependency
from app import database
from app.securities import create_access_token, pwd_context

from app.schema.user import User as ModelUser


from email_validator import validate_email, EmailNotValidError


router = APIRouter(tags=["Auth"])


@router.post("/login")
def login(username: str, password: str, db: DBDependency):

    user = database.get_user_by_username(db, username)
    if not user:
        raise HTTPException(401, detail={"message": "Invalid credentials"})

    if pwd_context.verify(password, user.hashed_password):
        token = create_access_token(uid=username)
        return {"access_token": token}

    raise HTTPException(401, detail={"message": "Invalid credentials"})


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


@router.post("/register", response_model=ModelUser)
async def register_user(form_data: RegisterRequest, db: DBDependency):
    try:
        valid = validate_email(form_data.email)
        form_data.email = valid.normalized  # Normalize the email
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email: {str(e)}"
        )
    hashed_password = pwd_context.hash(form_data.password)
    user = database.create_user(db=db, username=form_data.username, email=form_data.email,
                                hashed_password=hashed_password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return user
