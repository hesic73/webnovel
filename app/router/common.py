from fastapi import APIRouter

from app.dependencies import DBDependency

from app import database

from app.model.author import Author

router = APIRouter()


@router.get('/authors', response_model=list[Author])
async def get_authors(db: DBDependency):
    return database.get_authors(db)
