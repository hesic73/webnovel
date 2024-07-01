from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from webnovel_backend import database

DBDependency = Annotated[Session, Depends(database.get_db)]
