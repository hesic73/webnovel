from fastapi import APIRouter

from webnovel_backend.dependencies import DBDependency

from webnovel_backend import database

from webnovel_backend.model.author import Author, AuthorCreate
from webnovel_backend.model.novel import Novel, NovelCreate

router = APIRouter()


@router.post('/author', response_model=Author)
async def create_author(author: AuthorCreate, db: DBDependency):
    return database.create_author(db, author.name)


@router.post('/novel', response_model=Novel)
async def create_novel(novel: NovelCreate, db: DBDependency):
    tmp = database.create_novel(db=db, title=novel.title, author_name=novel.author_name,
                                genre=novel.genre, description=novel.description)
    return Novel(title=tmp.title, id=tmp.id, author_name=novel.author_name, author_id=tmp.author_id, genre=tmp.genre, description=tmp.description)
