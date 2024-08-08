from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.pages import pages_router

from app.utils.process_utils import executor_lifespan

from app.core.admin import initialize_admin
from app.core.auth import initialize_auth


from authx.exceptions import MissingTokenError, JWTDecodeError

app = FastAPI(title="网络小说阅读网站", lifespan=executor_lifespan)

initialize_admin(app)
initialize_auth(app)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router)
app.include_router(pages_router)


@app.exception_handler(MissingTokenError)
async def missing_token_error_handler(request: Request, exc: MissingTokenError):
    return JSONResponse(content={"detail": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(JWTDecodeError)
async def jwt_decode_error_handler(request: Request, exc: JWTDecodeError):
    return JSONResponse(content={"detail": str(exc)}, status_code=status.HTTP_401_UNAUTHORIZED)
