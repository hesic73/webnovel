from fastapi import Request, APIRouter, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import DBDependency
from app import database

from app.utils import convert_db_novel_to_model_novel

from app.schema.chapter import Chapter as ModelChapter

router = APIRouter(tags=["Pages"])

templates = Jinja2Templates(directory="templates")


def nl2br(value: str) -> str:
    return value.replace('\n', '<br>\n')


templates.env.filters['nl2br'] = nl2br

_DEFAULT_NOVEL_PAGE_SIZE = 10
_DEFAULT_CHAPTER_PAGE_SIZE = 100


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: DBDependency, page: int = Query(1, ge=1),
                page_size: int = Query(_DEFAULT_NOVEL_PAGE_SIZE, ge=1, le=100)):
    skip = (page - 1) * page_size

    novels = database.get_novels(db, skip=skip, limit=page_size)
    novels = [convert_db_novel_to_model_novel(db, novel) for novel in novels]

    total_novels = database.get_total_novels_count(
        db)
    total_pages = (total_novels + page_size - 1) // page_size

    return templates.TemplateResponse(
        request=request,
        name="index.html.jinja",
        context={
            'novels': novels,
            'page': page,
            'total_pages': total_pages,
            'page_size': page_size
        }
    )


@router.get("/novel/{id}/", response_class=HTMLResponse)
async def novel(request: Request, id: int, db: DBDependency):
    novel = database.get_novel(db, novel_id=id)
    novel = convert_db_novel_to_model_novel(db, novel)

    first_chapter = database.get_first_chapter(db, novel_id=id)
    first_chapter = ModelChapter(
        **first_chapter.__dict__) if first_chapter else None

    return templates.TemplateResponse(request=request, name="novel.html.jinja", context={
        'novel': novel,
        'title': f'{novel.title} - {novel.author_name}',
        'first_chapter': first_chapter,
    })


@router.get("/chapters_{id}/", response_class=HTMLResponse)
async def chapters(request: Request, id: int, db: DBDependency, page: int = Query(1, ge=1), page_size: int = Query(_DEFAULT_CHAPTER_PAGE_SIZE, ge=1, le=100)):
    skip = (page - 1) * page_size

    chapters = database.get_chapters(
        db, novel_id=id, skip=skip, limit=page_size)
    chapters = [ModelChapter(**chapter.__dict__) for chapter in chapters]
    # Add a function to get the total count of chapters for a novel
    total_chapters = database.get_total_chapters_count(db, novel_id=id)
    total_pages = (total_chapters + page_size - 1) // page_size

    novel = database.get_novel(db, novel_id=id)
    novel = convert_db_novel_to_model_novel(db, novel)

    return templates.TemplateResponse(
        request=request,
        name="chapters.html.jinja",
        context={
            'chapters': chapters,
            'page': page,
            'total_pages': total_pages,
            'page_size': page_size,
            'novel': novel,
            'title': f'{novel.title} - 章节目录',
        }
    )


@router.get("/novel/{novel_id}/{chapter_id}/", response_class=HTMLResponse)
async def chapter(request: Request, novel_id: int, chapter_id: int, db: DBDependency):
    novel = database.get_novel_with_chapters(db, novel_id=novel_id)
    if not novel:
        return HTMLResponse(status_code=404, content="Novel not found")

    chapter = next((ch for ch in novel.chapters if ch.id == chapter_id), None)
    if not chapter:
        return HTMLResponse(status_code=404, content="Chapter not found")

    chapter_model = ModelChapter(**chapter.__dict__)
    novel_model = convert_db_novel_to_model_novel(db, novel)

    previous_chapter = database.get_previous_chapter(
        db, novel_id, chapter.chapter_number)
    previous_chapter_model = ModelChapter(
        **previous_chapter.__dict__) if previous_chapter else None
    next_chapter = database.get_next_chapter(db, novel_id, chapter.chapter_number)
    next_chapter_model = ModelChapter(
        **next_chapter.__dict__) if next_chapter else None

    return templates.TemplateResponse(
        "chapter.html.jinja",
        {
            'request': request,
            'chapter': chapter_model,
            'novel': novel_model,
            'title': f'{novel.title} - {chapter.title}',
            'previous_chapter': previous_chapter_model,
            'next_chapter': next_chapter_model,
        }
    )


@router.get("/register_form/", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register_form.html.jinja", {
        "request": request,
        'title': '注册',
    })


@router.get("/login_form/", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login_form.html.jinja", {
        "request": request,
        'title': '登录',
    })


@router.get("/bookshelf/", response_class=HTMLResponse)
async def bookshelf(request: Request):
    return templates.TemplateResponse("bookshelf.html.jinja", {
        "request": request,
        'title': '书架',
    })
