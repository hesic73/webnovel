from fastapi import APIRouter

from webnovel_backend.dependencies import DBDependency

from webnovel_backend import database

from webnovel_backend.model.author import Author, AuthorCreate
from webnovel_backend.model.novel import Novel, NovelCreate

from webnovel_backend.utils import convert_db_novel_to_model_novel

router = APIRouter()


@router.post('/author', response_model=Author)
async def create_author(author: AuthorCreate, db: DBDependency):
    return database.create_author(db, author.name)


@router.post('/novel', response_model=Novel)
async def create_novel(novelCreate: NovelCreate, db: DBDependency):
    novel = database.create_novel(db=db, title=novelCreate.title, author_name=novelCreate.author_name,
                                  genre=novelCreate.genre, description=novelCreate.description)
    return convert_db_novel_to_model_novel(db, novel)
