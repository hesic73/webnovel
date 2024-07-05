import os

from passlib.context import CryptContext

from fastapi import FastAPI
from authx import AuthX, AuthXConfig, RequestToken


config = AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY=os.environ.get('SECRET_KEY', 'secret'),
    JWT_TOKEN_LOCATION=["headers"],
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
