from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .routes import common, lists, auth, admin


pages_router = APIRouter(
    include_in_schema=False,
    default_response_class=HTMLResponse)


pages_router.include_router(common.router)
pages_router.include_router(lists.router)
pages_router.include_router(auth.router)
pages_router.include_router(admin.router)
