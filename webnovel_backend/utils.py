from sqlalchemy.orm import Session

from webnovel_backend import database

from webnovel_backend.model.novel import Novel


def convert_db_novel_to_model_novel(db: Session, db_novel: database.Novel) -> Novel:
    # Fetch the author's name using the author_id
    db_author: database.Author = db.query(database.Author).filter(
        database.Author.id == db_novel.author_id).first()

    if not db_author:
        raise ValueError("Author not found")

    # Create the ModelNovel instance
    model_novel = Novel(
        title=db_novel.title,
        id=db_novel.id,
        author_name=db_author.name,
        author_id=db_novel.author_id,
        genre=db_novel.genre,
        description=db_novel.description
    )

    return model_novel
