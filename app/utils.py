from sqlalchemy.orm import Session


from app import database

from app.schema.novel import Novel as ModelNovel
from app.schema.author import Author as ModelAuthor


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
        author=ModelAuthor(
            id=db_author.id,
            name=db_author.name
        ),
        genre=db_novel.genre,
        description=db_novel.description
    )

    return model_novel
