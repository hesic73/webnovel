from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app import database

DBDependency = Annotated[Session, Depends(database.get_db)]
