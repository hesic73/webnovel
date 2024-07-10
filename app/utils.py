from sqlalchemy.orm import Session
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from authx.exceptions import MissingTokenError, JWTDecodeError

from app import database

from app.schema.novel import Novel as ModelNovel
from app.schema.author import Author as ModelAuthor

from app.enums import Genre, ScraperSource

from typing import Callable

import logging
import time

from concurrent.futures import ProcessPoolExecutor, Future
from contextlib import asynccontextmanager
from typing import Callable

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)


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


# Singleton executor instance
executor = ProcessPoolExecutor()


def submit_task(fn: Callable, *args, **kwargs) -> Future:
    """Wrapper around the executor submit method"""
    return executor.submit(fn, *args, **kwargs)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up")
    yield
    logging.info("Shutting down executor")
    executor.shutdown(wait=True)
    logging.info("Shutdown complete")


templates = Jinja2Templates(directory="templates")


def nl2br(value: str) -> str:
    return value.replace('\n', '<br>\n')


templates.env.filters['nl2br'] = nl2br


class PageErrorException(Exception):
    def __init__(self, status_code: int, title: str, message: str | None = None):
        self.status_code = status_code
        self.title = title
        self.message = message


def initialize_exception_handler(app: FastAPI):
    @app.exception_handler(PageErrorException)
    async def page_error_exception_handler(request: Request, exc: PageErrorException):
        return templates.TemplateResponse(
            "error.html.jinja",
            {
                "request": request,
                "title": exc.title,
                "message": exc.message
            },
            status_code=exc.status_code
        )

    @app.exception_handler(MissingTokenError)
    async def missing_token_error_handler(request: Request, exc: MissingTokenError):
        return JSONResponse(content={"detail": str(exc)}, status_code=401)

    @app.exception_handler(JWTDecodeError)
    async def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
        return JSONResponse(content={"detail": str(exc)}, status_code=401)
