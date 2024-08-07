from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


def nl2br(value: str) -> str:
    return value.replace('\n', '<br>\n')


templates.env.filters['nl2br'] = nl2br
