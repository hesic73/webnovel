from fastapi import Request, APIRouter, Query
from fastapi import status

from pydantic import BaseModel

from .templates import templates

from app.utils.model_utils import convert_db_novel_to_model_novel, convert_db_chapter_to_model_chapter
from app.consts import DEFAULT_NOVEL_PAGE_SIZE

from app.schemas import AuthorNovelEntry
from app.database.session import DBDependency
from app import database


router = APIRouter()


@router.get("/novels/")
async def novels(request: Request, db: DBDependency, page: int = Query(1, ge=1)):
    page_size = DEFAULT_NOVEL_PAGE_SIZE
    skip = (page - 1) * page_size

    novels = database.get_novels(db, skip=skip, limit=page_size)
    novels = [convert_db_novel_to_model_novel(db, novel) for novel in novels]

    total_novels = database.get_total_novels_count(
        db)
    total_pages = (total_novels + page_size - 1) // page_size

    return templates.TemplateResponse(
        request=request,
        name="novels.html.jinja",
        context={
            'novels': novels,
            'page': page,
            'total_pages': total_pages,
            'page_size': page_size
        }
    )


@router.get("/author/{author_id}/")
async def author(request: Request, author_id: int, db: DBDependency):
    author = database.get_author_with_novels(db, author_id)
    if not author:
        return templates.TemplateResponse(
            "error.html.jinja",
            {
                "request": request,
                "title": "Author not found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    novels = author.novels
    latest_chapters = [database.get_last_chapter(
        db, novel_id=novel.id) for novel in novels]

    entries = [AuthorNovelEntry(novel=convert_db_novel_to_model_novel(db, novel), latest_chapter=convert_db_chapter_to_model_chapter(
        chapter) if chapter else None) for novel, chapter in zip(novels, latest_chapters)]

    return templates.TemplateResponse("author.html.jinja", {
        'request': request,
        'author': author,
        'entries': entries,
        'title': f"{author.name} - 作品列表",
    })
