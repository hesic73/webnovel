from fastapi import FastAPI

from sqlalchemy.orm import Session

from sqladmin import Admin, ModelView


from app import database

from app.model.novel import Novel as ModelNovel


def convert_db_novel_to_model_novel(db: Session, db_novel: database.Novel) -> ModelNovel:
    # Fetch the author's name using the author_id
    db_author: database.Author = db.query(database.Author).filter(
        database.Author.id == db_novel.author_id).first()

    if not db_author:
        raise ValueError("Author not found")

    # Create the ModelNovel instance
    model_novel = ModelNovel(
        title=db_novel.title,
        id=db_novel.id,
        author_name=db_author.name,
        author_id=db_novel.author_id,
        genre=db_novel.genre,
        description=db_novel.description
    )

    return model_novel


class AuthorView(ModelView, model=database.Author):
    column_list = [database.Author.id, database.Author.name]


class NovelView(ModelView, model=database.Novel):
    column_list = [database.Novel.id, database.Novel.title,
                   database.Novel.genre]


class ChapterView(ModelView, model=database.Chapter):
    column_list = [database.Chapter.id, database.Chapter.title,
                   database.Chapter.chapter_number, database.Chapter.novel_id]


def initialize_admin(app: FastAPI):
    admin = Admin(app=app, engine=database.engine, title="Admin Panel")
    admin.add_view(AuthorView)
    admin.add_view(NovelView)
    admin.add_view(ChapterView)
    return admin
