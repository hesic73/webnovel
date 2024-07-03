from fastapi import Request, APIRouter, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import DBDependency
from app import database

from app.utils import convert_db_novel_to_model_novel

router = APIRouter()

templates = Jinja2Templates(directory="templates")

_DEFAULT_PAGE_SIZE = 10


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: DBDependency, page: int = Query(1, ge=1),
                page_size: int = Query(_DEFAULT_PAGE_SIZE, ge=1, le=100)):
    skip = (page - 1) * page_size

    novels = database.get_novels(db, skip=skip, limit=page_size)
    novels = [convert_db_novel_to_model_novel(db, novel) for novel in novels]

    total_novels = database.get_total_novels_count(
        db)
    total_pages = (total_novels + page_size - 1) // page_size

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            'novels': novels,
            'page': page,
            'total_pages': total_pages,
            'page_size': _DEFAULT_PAGE_SIZE
        }
    )


@router.get("/novel/{id}/", response_class=HTMLResponse)
async def novel(request: Request, id: int, db: DBDependency):
    novel = database.get_novel(db, novel_id=id)
    novel = convert_db_novel_to_model_novel(db, novel)
    return templates.TemplateResponse(request=request, name="novel.html", context={
        'novel': novel,
        'chapters': []
    })
