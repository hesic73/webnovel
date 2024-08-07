from sqlalchemy.orm import Session


from app import database
from app import schemas


def convert_db_novel_to_model_novel(db: Session, db_novel: database.Novel) -> schemas.Novel:
    # Fetch the author's name using the author_id
    db_author: database.Author = db.query(database.Author).filter(
        database.Author.id == db_novel.author_id).first()

    if not db_author:
        raise ValueError("Author not found")

    # Create the ModelNovel instance
    model_novel = schemas.Novel(
        title=db_novel.title,
        id=db_novel.id,
        author_name=db_author.name,
        author=schemas.Author(
            id=db_author.id,
            name=db_author.name
        ),
        genre=db_novel.genre,
        description=db_novel.description
    )

    return model_novel


def convert_db_chapter_to_model_chapter(db_chapter: database.Chapter) -> schemas.Chapter:
    return schemas.Chapter(
        id=db_chapter.id,
        novel_id=db_chapter.novel_id,
        title=db_chapter.title,
        content=db_chapter.content
    )
