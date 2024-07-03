from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import DBDependency
from app import database

from app.utils import convert_db_novel_to_model_novel

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: DBDependency):
    novels = database.get_novels(db)
    novels = [convert_db_novel_to_model_novel(db, novel) for novel in novels]
    return templates.TemplateResponse(
        request=request, name="index.html", context={'novels': novels})


@router.get("/novel/{id}/", response_class=HTMLResponse)
async def novel(request: Request, id: int, db: DBDependency):
    novel = database.get_novel(db, novel_id=id)
    novel = convert_db_novel_to_model_novel(db, novel)
    return templates.TemplateResponse(request=request, name="novel.html", context={
        'novel': novel,
        'chapters': []
    })
