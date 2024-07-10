from fastapi import Request, APIRouter, Query
from fastapi.responses import HTMLResponse


from app.database import DBDependency
from app import database

from app.utils import convert_db_novel_to_model_novel, templates, PageErrorException
from app.enums import Genre, ScraperSource

from app.schema.chapter import Chapter as ModelChapter

router = APIRouter(tags=["Pages"])


_DEFAULT_NOVEL_PAGE_SIZE = 20
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

    if not novel:
        raise PageErrorException(404, "Novel not found")

    novel = convert_db_novel_to_model_novel(db, novel)

    first_chapter = database.get_first_chapter(db, novel_id=id)
    first_chapter = ModelChapter(
        **first_chapter.__dict__) if first_chapter else None

    return templates.TemplateResponse(request=request, name="novel.html.jinja", context={
        'novel': novel,
        'title': f'{novel.title} - {novel.author.name}',
        'first_chapter': first_chapter,
    })


@router.get("/novel/{id}/chapters/", response_class=HTMLResponse)
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


@router.get("/novel/{novel_id}/{chapter_id}.html", response_class=HTMLResponse)
async def chapter(request: Request, novel_id: int, chapter_id: int, db: DBDependency):
    novel = database.get_novel_with_chapters(db, novel_id=novel_id)
    if not novel:
        raise PageErrorException(404, "Novel not found")

    chapter = next((ch for ch in novel.chapters if ch.id == chapter_id), None)
    if not chapter:
        raise PageErrorException(404, "Chapter not found")

    chapter_model = ModelChapter(**chapter.__dict__)
    novel_model = convert_db_novel_to_model_novel(db, novel)

    previous_chapter = database.get_previous_chapter(
        db, novel_id, chapter.chapter_number)
    previous_chapter_model = ModelChapter(
        **previous_chapter.__dict__) if previous_chapter else None
    next_chapter = database.get_next_chapter(
        db, novel_id, chapter.chapter_number)
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


@router.get("/register_form.html", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register_form.html.jinja", {
        "request": request,
        'title': '注册',
    })


@router.get("/login_form.html", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login_form.html.jinja", {
        "request": request,
        'title': '登录',
    })


@router.get("/bookshelf/", response_class=HTMLResponse)
async def bookshelf(request: Request):
    return templates.TemplateResponse("bookshelf.html.jinja", {
        "request": request,
        'title': '书架',
    })


@router.get("/author/{author_id}/", response_class=HTMLResponse)
async def author(request: Request, author_id: int, db: DBDependency):
    author = database.get_author_with_novels(db, author_id)
    if not author:
        raise PageErrorException(404, "Author not found")

    novels = author.novels
    novels = [convert_db_novel_to_model_novel(db, novel) for novel in novels]

    return templates.TemplateResponse("author.html.jinja", {
        'request': request,
        'author': author,
        'novels': novels,
        'title': f"{author.name} - 作品列表",
    })


@router.get("/scrape_form.html", response_class=HTMLResponse)
async def scrape_form(request: Request):
    return templates.TemplateResponse("scrape_form.html.jinja", {
        "request": request,
        "title": "爬取小说",
        "genres": Genre,
        "sources": ScraperSource
    })
