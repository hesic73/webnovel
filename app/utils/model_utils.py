from app.database import Novel, Chapter
from app import schemas


def map_db_novel_to_schema(db_novel: Novel) -> schemas.Novel:

    model_novel = schemas.Novel(
        title=db_novel.title,
        id=db_novel.id,
        author_name=db_novel.author.name,
        author=schemas.Author(
            id=db_novel.author.id,
            name=db_novel.author.name
        ),
        genre=db_novel.genre,
        description=db_novel.description
    )

    return model_novel


def map_db_chapter_to_schema(db_chapter: Chapter) -> schemas.Chapter:
    return schemas.Chapter(
        id=db_chapter.id,
        novel_id=db_chapter.novel_id,
        title=db_chapter.title,
        content=db_chapter.content
    )
