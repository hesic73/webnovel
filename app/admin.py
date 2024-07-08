import os

from fastapi import FastAPI

from starlette.requests import Request
from starlette.responses import RedirectResponse

from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend


from app import database
from app.securities import create_access_token, verify_token, pwd_context
from app.enums import UserType


class AuthorView(ModelView, model=database.Author):
    column_list = [database.Author.id, database.Author.name]


class NovelView(ModelView, model=database.Novel):
    column_list = [database.Novel.id, database.Novel.title,
                   database.Novel.genre]

    form_excluded_columns = [database.Novel.chapters,
                             database.Novel.reading_entries]

    column_details_exclude_list = [database.Novel.author_id,]


class ChapterView(ModelView, model=database.Chapter):
    column_list = [database.Chapter.id, database.Chapter.title,
                   database.Chapter.chapter_number, database.Chapter.novel_id]


class UserView(ModelView, model=database.User):
    column_list = [database.User.id, database.User.username,
                   database.User.email, database.User.user_type]


class ReadingEntryView(ModelView, model=database.ReadingEntry):
    column_list = [database.ReadingEntry.id, database.ReadingEntry.user_id,
                   database.ReadingEntry.novel_id, database.ReadingEntry.current_chapter_id]


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        # Get the database
        with database.SessionLocal() as db:
            user = database.get_user_by_username(db, username)

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

    admin = Admin(app=app, engine=database.engine,
                  authentication_backend=authentication_backend)
    admin.add_view(AuthorView)
    admin.add_view(NovelView)
    admin.add_view(ChapterView)
    admin.add_view(UserView)
    admin.add_view(ReadingEntryView)
    return admin
