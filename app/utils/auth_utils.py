import os

from passlib.context import CryptContext

from fastapi import FastAPI, Depends, HTTPException
from authx import AuthX, AuthXConfig, RequestToken, TokenPayload

from typing import Annotated

from app import database
from app.database.session import DBDependency
from app.enums import UserType

config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=os.environ.get('SECRET_KEY', 'secret'),
    JWT_TOKEN_LOCATION=["headers"],
    JWT_ACCESS_TOKEN_EXPIRES=None,
)

auth = AuthX(config=config)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def initialize_auth(app: FastAPI):
    auth.handle_errors(app)


def create_access_token(uid: str):
    return auth.create_access_token(uid=uid)


def verify_token(token: str):
    request_token = RequestToken(token=token, location="headers")

    try:
        payload = auth.verify_token(request_token)
    except Exception as e:
        return False

    return True


RequestTokenDependency = Annotated[RequestToken, Depends(
    auth.get_access_token_from_request)]


TokenPayloadDependency = Annotated[TokenPayload,
                                   Depends(auth.access_token_required)]


async def require_admin(payload: TokenPayloadDependency, db: DBDependency):
    username = payload.sub
    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    return user


RequireAdminDependency = Annotated[database.User, Depends(require_admin)]


async def require_user(payload: TokenPayloadDependency, db: DBDependency):
    username = payload.sub
    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


RequireUserDependency = Annotated[database.User, Depends(require_user)]
