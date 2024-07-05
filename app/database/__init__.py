from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base
from .novel import *
from .chapter import *
from .author import *
from .user import *
from .reading_entry import *

SQLALCHEMY_DATABASE_URL = "sqlite:///./webnovel.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)


DBDependency = Annotated[Session, Depends(get_db)]
