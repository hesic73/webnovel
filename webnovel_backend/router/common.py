from fastapi import APIRouter

from webnovel_backend.dependencies import DBDependency

from webnovel_backend import database

from webnovel_backend.model.author import Author

router = APIRouter()


@router.get('/authors', response_model=list[Author])
async def get_authors(db: DBDependency):
    return database.get_authors(db)
