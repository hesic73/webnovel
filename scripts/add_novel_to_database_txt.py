from app.database.session import get_db_sync
from app.enums import Genre
from app.database import crud
from sqlalchemy.orm import Session
import re
import click
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Ensure you have a function to get a database session


def parse_novel_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Extract title and author
    title_author_pattern = r"^(.*?)\s*作者：(.*?)$"
    title_author_match = re.search(title_author_pattern, lines[0])
    if not title_author_match:
        raise ValueError("Title and author information not found in the file.")

    title = title_author_match.group(1).strip()
    author = title_author_match.group(2).strip()

    # Extract description
    description = ""
    description_start = False
    chapters = []
    chapter_title = None
    chapter_content = []

    for line in lines[1:]:
        stripped_line = line.strip()
        if stripped_line.startswith("内容简介："):
            description_start = True
            description = stripped_line.replace("内容简介：", "").strip()
            continue
        if description_start and not stripped_line:
            description_start = False
            continue
        if description_start:
            description += "\n" + stripped_line
            continue

        if stripped_line.startswith("第") and "章" in stripped_line and not line.startswith(" "):
            if chapter_title:
                chapters.append({
                    'title': chapter_title,
                    'content': "\n".join(chapter_content).strip()
                })
                chapter_content = []
            chapter_title = stripped_line
        else:
            if stripped_line:
                chapter_content.append(stripped_line)

    if chapter_title:
        chapters.append({
            'title': chapter_title,
            'content': "\n".join(chapter_content).strip()
        })

    parsed_chapters = []
    for i, chapter in enumerate(chapters, start=1):
        parsed_chapters.append({
            'number': i,
            'title': chapter['title'],
            'content': chapter['content']
        })

    return {
        'title': title,
        'author': author,
        'description': description,
        'chapters': parsed_chapters
    }


def add_novel_to_database_txt(db: Session, file_path: str, genre: Genre):
    novel_data = parse_novel_file(file_path)

    novel = crud.create_novel(
        db=db,
        title=novel_data['title'],
        author_name=novel_data['author'],
        genre=genre,
        description=novel_data['description']
    )

    for chapter in novel_data['chapters']:
        crud.create_chapter(
            db=db,
            novel_id=novel.id,
            chapter_number=chapter['number'],
            title=chapter['title'],
            content=chapter['content']
        )

    return novel


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.argument('genre', type=click.Choice([genre.value for genre in Genre]))
def cli(file_path, genre):
    """CLI tool to add a novel from a txt file to the database."""
    db = next(get_db_sync())
    genre_enum = Genre(genre)
    novel = add_novel_to_database_txt(db, file_path, genre_enum)
    click.echo(
        f"Novel '{novel.title}' by {novel.author.name} has been added to the database.")


if __name__ == '__main__':
    cli()
