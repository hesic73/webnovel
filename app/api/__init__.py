from fastapi import APIRouter

from .routes import bookshelf, auth, scrapers

api_router = APIRouter(prefix="/api")

api_router.include_router(bookshelf.router, tags=["bookshelf"])
api_router.include_router(auth.router, prefix='/auth', tags=["auth"])
api_router.include_router(
    scrapers.router, tags=["scrapers"])
