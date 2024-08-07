from fastapi import Request, APIRouter

from .templates import templates


router = APIRouter()


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
