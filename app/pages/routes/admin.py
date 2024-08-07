from fastapi import Request, APIRouter

from app.enums import Genre, ScraperSource


from .templates import templates


router = APIRouter()


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
