from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse

from fastapi import status


from app.database.session import DBDependency
from app.database import crud

from app.utils.model_utils import convert_db_novel_to_model_novel, convert_db_chapter_to_model_chapter


from app.consts import LATEST_CHAPTERS_LIMIT

from .templates import templates


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    return RedirectResponse("/novels/")


@router.get("/novel/{id}/")
async def novel(request: Request, id: int, db: DBDependency):
    novel = crud.get_novel(db, novel_id=id)

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

    first_chapter = crud.get_first_chapter(db, novel_id=id)
    first_chapter = convert_db_chapter_to_model_chapter(
        first_chapter) if first_chapter else None

    last_chapter = crud.get_last_chapter(db, novel_id=id)
    last_chapter = convert_db_chapter_to_model_chapter(
        last_chapter) if last_chapter else None

    latest_chapters = crud.get_chapters_reversed(
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
    chapters = crud.get_all_chapters(
        db, novel_id=id)
    chapters = [convert_db_chapter_to_model_chapter(
        chapter) for chapter in chapters]
    # Add a function to get the total count of chapters for a novel
    # total_chapters = crud.get_total_chapters_count(db, novel_id=id)

    novel = crud.get_novel(db, novel_id=id)
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
    novel = crud.get_novel_with_chapters(db, novel_id=novel_id)
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

    previous_chapter = crud.get_previous_chapter(
        db, novel_id, chapter.chapter_number)
    previous_chapter_model = convert_db_chapter_to_model_chapter(
        previous_chapter) if previous_chapter else None
    next_chapter = crud.get_next_chapter(
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


@router.get("/bookshelf/")
async def bookshelf(request: Request):
    return templates.TemplateResponse("bookshelf.html.jinja", {
        "request": request,
        'title': '书架',
    })
