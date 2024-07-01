from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .base import Base
from .novel import *
from .chapter import *
from .author import *

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

Base.metadata.create_all(bind=engine)
