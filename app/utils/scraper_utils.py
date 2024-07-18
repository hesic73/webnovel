from sqlalchemy.orm import Session

from typing import Callable
import time
import logging


from app.enums import ScraperSource, Genre

from app import database


logger = logging.getLogger(__name__)


def make_scraper_function(source: ScraperSource):
    match source:
        case ScraperSource.BIQUGE1:
            from app.spiders.biquge1 import get_novel_data, get_chapter_content
        case ScraperSource.BIQUGE2:
            from app.spiders.biquge2 import get_novel_data, get_chapter_content
        case ScraperSource.PIAOTIAN:
            from app.spiders.piaotian import get_novel_data, get_chapter_content
        case _:
            raise ValueError(f"Invalid source: {source}")

    def add_novel_to_database(db: Session, novel_url: str, genre: Genre, post_get_novel_data: Callable[[dict], None] = None, on_chapter_update: Callable[[int], None] = None, sleep_seconds: float = 0.2):
        novel_data = get_novel_data(novel_url)

        if post_get_novel_data:
            post_get_novel_data(novel_data)

        # Create novel entry
        novel = database.create_novel(
            db=db,
            title=novel_data['title'],
            author_name=novel_data['author'],
            genre=genre,
            description=novel_data['intro']
        )

        if novel is None:
            raise ValueError(f"Error creating novel {novel_data['title']}.")

        # Add chapters
        for i, chapter in enumerate(novel_data['chapters']):
            chapter_title, chapter_url = chapter

            logger.info(
                f"Adding chapter {chapter_title} ({i + 1}/{len(novel_data['chapters'])})")

            try:
                chapter_content = get_chapter_content(chapter_url)
            except Exception as e:
                logger.error(
                    f"Error getting chapter content for {chapter_url}: {e}")
                continue

            database.create_chapter(
                db=db,
                novel_id=novel.id,
                chapter_number=i + 1,
                title=chapter_title,
                content=chapter_content
            )

            if on_chapter_update:
                on_chapter_update(i + 1)

            # Sleep between requests to avoid overloading the server
            time.sleep(sleep_seconds)

        return novel

    return add_novel_to_database
