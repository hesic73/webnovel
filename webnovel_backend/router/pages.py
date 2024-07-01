from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from webnovel_backend.model.novel import Novel
from webnovel_backend.dependencies import DBDependency
from webnovel_backend import database

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: DBDependency):
    novels = database.get_novels(db)
    return templates.TemplateResponse(
        request=request, name="index.html", context={'novels': novels})


@router.get("/novel/{id}/", response_class=HTMLResponse)
async def novel(request: Request, id: int, db: DBDependency):
    novel = database.get_novel(db, novel_id=id)
    return templates.TemplateResponse(request=request, name="novel.html", context={
        'novel': novel,
        'chapters': []
    })
