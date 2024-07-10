from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.router import api, pages, auth, admin_api

from app.utils import lifespan

from app.admin import initialize_admin
from app.securities import initialize_auth

app = FastAPI(title="网络小说阅读网站", lifespan=lifespan)

initialize_admin(app)
initialize_auth(app)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(api.router, prefix="/api")

app.include_router(admin_api.router, prefix="/admin_api")
