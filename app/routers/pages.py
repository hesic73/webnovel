from fastapi import Request, APIRouter, Query
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi import status

from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


from app.database import DBDependency
from app import database

from app.utils.model_utils import convert_db_novel_to_model_novel, convert_db_chapter_to_model_chapter
from app.enums import Genre, ScraperSource


from app import models

from app.consts import DEFAULT_NOVEL_PAGE_SIZE, LATEST_CHAPTERS_LIMIT


templates = Jinja2Templates(directory="templates")


def nl2br(value: str) -> str:
    return value.replace('\n', '<br>\n')


templates.env.filters['nl2br'] = nl2br

router = APIRouter(tags=["Pages"], include_in_schema=False,
                   default_response_class=HTMLResponse)


@router.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse("/novels/")


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


@router.get("/novel/{id}/")
async def novel(request: Request, id: int, db: DBDependency):
    novel = database.get_novel(db, novel_id=id)

    if not novel:
        return templates.TemplateResponse(
            "error.html.jinja",
            {
                "request": request,
                "title": "Novel not found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    novel = convert_db_novel_to_model_novel(db, novel)

    first_chapter = database.get_first_chapter(db, novel_id=id)
    first_chapter = convert_db_chapter_to_model_chapter(
        first_chapter) if first_chapter else None

    last_chapter = database.get_last_chapter(db, novel_id=id)
    last_chapter = convert_db_chapter_to_model_chapter(
        last_chapter) if last_chapter else None

    latest_chapters = database.get_chapters_reversed(
        db, novel_id=id, limit=LATEST_CHAPTERS_LIMIT)
    latest_chapters = [convert_db_chapter_to_model_chapter(chapter) if chapter else None
                       for chapter in latest_chapters]

    return templates.TemplateResponse(request=request, name="novel.html.jinja", context={
        'novel': novel,
        'title': f'{novel.title} - {novel.author.name}',
        'first_chapter': first_chapter,
        'last_chapter': last_chapter,
        'latest_chapters': latest_chapters,
    })


@router.get("/novel/{id}/chapters/")
async def chapters(request: Request, id: int, db: DBDependency):
    chapters = database.get_all_chapters(
        db, novel_id=id)
    chapters = [convert_db_chapter_to_model_chapter(
        chapter) for chapter in chapters]
    # Add a function to get the total count of chapters for a novel
    # total_chapters = database.get_total_chapters_count(db, novel_id=id)

    novel = database.get_novel(db, novel_id=id)
    novel = convert_db_novel_to_model_novel(db, novel)

    return templates.TemplateResponse(
        request=request,
        name="chapters.html.jinja",
        context={
            'chapters': chapters,
            'novel': novel,
            'title': f'{novel.title} - 章节目录',
        }
    )


@router.get("/novel/{novel_id}/{chapter_id}.html")
async def chapter(request: Request, novel_id: int, chapter_id: int, db: DBDependency):
    novel = database.get_novel_with_chapters(db, novel_id=novel_id)
    if not novel:
        return templates.TemplateResponse(
            "error.html.jinja",
            {
                "request": request,
                "title": "Novel not found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    chapter = next((ch for ch in novel.chapters if ch.id == chapter_id), None)
    if not chapter:
        return templates.TemplateResponse(
            "error.html.jinja",
            {
                "request": request,
                "title": "Chapter not found",
            },
            status_code=status.HTTP_404_NOT_FOUND,
        )

    chapter_model = convert_db_chapter_to_model_chapter(chapter)
    novel_model = convert_db_novel_to_model_novel(db, novel)

    previous_chapter = database.get_previous_chapter(
        db, novel_id, chapter.chapter_number)
    previous_chapter_model = convert_db_chapter_to_model_chapter(
        previous_chapter) if previous_chapter else None
    next_chapter = database.get_next_chapter(
        db, novel_id, chapter.chapter_number)
    next_chapter_model = convert_db_chapter_to_model_chapter(
        next_chapter) if next_chapter else None

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


@router.get("/register_form.html")
async def register_form(request: Request):
    return templates.TemplateResponse("auth/register_form.html.jinja", {
        "request": request,
        'title': '注册',
    })


@router.get("/login_form.html")
async def login_form(request: Request):
    return templates.TemplateResponse("auth/login_form.html.jinja", {
        "request": request,
        'title': '登录',
    })


@router.get("/bookshelf/")
async def bookshelf(request: Request):
    return templates.TemplateResponse("bookshelf.html.jinja", {
        "request": request,
        'title': '书架',
    })


class AuthorNovelEntry(BaseModel):
    novel: models.Novel
    latest_chapter: models.Chapter | None


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


@router.get("/admin-panel.html")
async def admin_panel(request: Request):
    return templates.TemplateResponse("admin/panel.html.jinja", {
        "request": request,
        'title': '管理面板',
    })


@router.get("/scrape-form.html")
async def scrape_form(request: Request):
    return templates.TemplateResponse("admin/scrape_form.html.jinja", {
        "request": request,
        "title": "爬取小说",
        "genres": Genre,
        "sources": ScraperSource
    })
