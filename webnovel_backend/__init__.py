from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from webnovel_backend.router import pages, common, admin

app = FastAPI(title="网络小说阅读网站")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(common.router)
app.include_router(admin.router, prefix='/admin')
