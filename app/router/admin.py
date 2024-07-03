from fastapi import APIRouter

from app.dependencies import DBDependency

from app import database

from app.model.author import Author, AuthorCreate
from app.model.novel import Novel, NovelCreate

from app.utils import convert_db_novel_to_model_novel

router = APIRouter()


@router.post('/author', response_model=Author)
async def create_author(author: AuthorCreate, db: DBDependency):
    return database.create_author(db, author.name)


@router.post('/novel', response_model=Novel)
async def create_novel(novelCreate: NovelCreate, db: DBDependency):
    novel = database.create_novel(db=db, title=novelCreate.title, author_name=novelCreate.author_name,
                                  genre=novelCreate.genre, description=novelCreate.description)
    return convert_db_novel_to_model_novel(db, novel)
