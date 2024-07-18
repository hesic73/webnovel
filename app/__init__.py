from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routers import api, internal, pages, auth

from app.utils.process_utils import executor_lifespan

from app.admin import initialize_admin
from app.utils.auth_utils import initialize_auth


from authx.exceptions import MissingTokenError, JWTDecodeError

app = FastAPI(title="网络小说阅读网站", lifespan=executor_lifespan)

initialize_admin(app)
initialize_auth(app)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(api.router, prefix="/api")
app.include_router(internal.router, prefix="/internal")


@app.exception_handler(MissingTokenError)
async def missing_token_error_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(content={"detail": str(exc)}, status_code=401)


@app.exception_handler(JWTDecodeError)
async def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(content={"detail": str(exc)}, status_code=401)
