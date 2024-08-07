from fastapi import APIRouter
from concurrent.futures import Future
import logging


from pydantic import BaseModel

from app.database.session import get_db_sync
from app.utils.auth_utils import RequireAdminDependency

from app.enums import Genre, ScraperSource

from app.utils.scraper_utils import make_scraper_function
from app.utils.process_utils import submit_task


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ScrapeNovel(BaseModel):
    url: str
    source: ScraperSource
    genre: Genre


router = APIRouter()


def add_novel_to_database_wrapper(scrape_novel: ScrapeNovel):
    db = next(get_db_sync())
    try:
        add_novel_to_database = make_scraper_function(scrape_novel.source)
        add_novel_to_database(db=db, novel_url=scrape_novel.url,
                              genre=scrape_novel.genre)
    finally:
        db.close()


@router.post("/scrape/")
async def scraper(scrape_novel: ScrapeNovel, user: RequireAdminDependency):

    logger.info(f"Received request to scrape: {scrape_novel.url}")
    future = submit_task(add_novel_to_database_wrapper, scrape_novel)

    def log_result(f: Future[None]):
        try:
            result = f.result()
            logger.info(f"Scraping completed: {result}")
        except Exception as e:
            logger.error(f"Error during scraping: {e}")

    future.add_done_callback(log_result)
    return {"message": "Scraping started"}
