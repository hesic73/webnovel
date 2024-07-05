from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.router import pages

from app.utils import initialize_admin

app = FastAPI(title="网络小说阅读网站")

initialize_admin(app)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
