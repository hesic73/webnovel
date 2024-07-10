from fastapi import HTTPException, Request, APIRouter, Query, Depends
from concurrent.futures import ProcessPoolExecutor, Future
import logging

from pydantic import BaseModel

from app.database import DBDependency, get_db_sync
from app.securities import TokenPayloadDependency
from app import database

from app.enums import Genre, ScraperSource, UserType

from app.utils import make_scraper_function


class ScrapeNovel(BaseModel):
    url: str
    source: ScraperSource
    genre: Genre


router = APIRouter(tags=["Admin API"])

executor = ProcessPoolExecutor()


def add_novel_to_database_wrapper(scrape_novel: ScrapeNovel):
    db = next(get_db_sync())
    try:
        add_novel_to_database = make_scraper_function(scrape_novel.source)
        add_novel_to_database(db=db, novel_url=scrape_novel.url,
                              genre=scrape_novel.genre)
    finally:
        db.close()


@router.post("/scrape/")
async def scraper(scrape_novel: ScrapeNovel, db: DBDependency, payload: TokenPayloadDependency):

    username = payload.sub

    user = database.get_user_by_username(db=db, username=username)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.user_type != UserType.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")

    logging.info(f"Received request to scrape: {scrape_novel.url}")
    future = executor.submit(add_novel_to_database_wrapper, scrape_novel)

    def log_result(f: Future[None]):
        try:
            result = f.result()
            logging.info(f"Scraping completed: {result}")
        except Exception as e:
            logging.error(f"Error during scraping: {e}")

    future.add_done_callback(log_result)
    return {"message": "Scraping started"}
