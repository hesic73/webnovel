import os

from fastapi import FastAPI

from starlette.requests import Request
from starlette.responses import RedirectResponse

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend


from app.database import crud, engine, Author, Novel, Chapter, User, ReadingEntry
from app.database.session import SessionLocal
from app.utils.auth_utils import create_access_token, verify_token, pwd_context
from app.enums import UserType


class AuthorView(ModelView, model=Author):
    column_list = [Author.id, Author.name]


class NovelView(ModelView, model=Novel):
    column_list = [Novel.id, Novel.title,
                   Novel.genre]

    form_excluded_columns = [Novel.chapters,
                             Novel.reading_entries]

    column_details_exclude_list = [Novel.author_id,]


class ChapterView(ModelView, model=Chapter):
    column_list = [Chapter.id, Chapter.title,
                   Chapter.chapter_number, Chapter.novel_id]


class UserView(ModelView, model=User):
    column_list = [User.id, User.username,
                   User.email, User.user_type]


class ReadingEntryView(ModelView, model=ReadingEntry):
    column_list = [ReadingEntry.id, ReadingEntry.user_id,
                   ReadingEntry.novel_id, ReadingEntry.current_chapter_id]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Get the database
        with SessionLocal() as db:
            user = crud.get_user_by_username(db, username)

        if not user:
            return False

        if user.user_type != UserType.ADMIN:
            return False

        # Validate username/password credentials
        if pwd_context.verify(password, user.hashed_password):
            # Create a token
            token = create_access_token(uid=username)
            # Update session
            request.session.update({"token": token})
            return True

        return False

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        return verify_token(token)


def initialize_admin(app: FastAPI):

    authentication_backend = AdminAuth(
        secret_key=os.environ.get('SECRET_KEY', 'secret'))

    admin = Admin(app=app, engine=engine,
                  authentication_backend=authentication_backend)
    admin.add_view(AuthorView)
    admin.add_view(NovelView)
    admin.add_view(ChapterView)
    admin.add_view(UserView)
    admin.add_view(ReadingEntryView)
    return admin
