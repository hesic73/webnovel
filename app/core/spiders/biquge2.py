"""
https://bqghh.cc
"""

import logging
import requests
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def search_book(book_name: str, biquge_url: str) -> str:
    search_url_base = urljoin(biquge_url, "/user/search.html")
    query_params = {'q': book_name}
    query_string = urlencode(query_params)
    search_url = f"{search_url_base}?{query_string}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    results = requests.get(search_url, headers=headers, timeout=5.0).json()

    for result in results:
        novel_name = result['articlename']
        novel_author = result['author']
        novel_url = result['url_list']

        if novel_name == book_name:
            logger.info(f'Found novel:{novel_name} author:{novel_author}')
            return urljoin(biquge_url, novel_url)

    raise Exception('No novels found')


def get_novel_data(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    html = requests.get(url, headers=headers, timeout=5.0).text
    soup = BeautifulSoup(html, 'html.parser')

    # Extract novel info
    info = soup.find('div', class_='info')
    novel_name = info.find('h1').text
    author_name = info.find('div', class_='small').find(
        'span').text.replace('作者：', '')
    intro = info.find('div', class_='intro').find('dd').text.strip()

    # Extract chapters list
    chapters_list = soup.find('div', class_='listmain').find('dl')
    chapters = []
    for chapter in chapters_list.find_all('dd'):
        # Skip <dd> elements with class "more pc_none"
        if chapter.get('class', []):
            continue
        chapter_title = chapter.find('a').text
        chapter_url = urljoin(url, chapter.find('a')['href'])
        chapters.append((chapter_title, chapter_url))
    return {
        'title': novel_name,
        'author': author_name,
        'intro': intro,
        'chapters': chapters
    }


def get_chapter_content(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    html = requests.get(url, headers=headers, timeout=5.0).text
    soup = BeautifulSoup(html, 'html.parser')
    content_div = soup.find('div', id='chaptercontent')

    # Remove the <p> element at the end
    if content_div.find('p', class_='readinline'):
        content_div.find('p', class_='readinline').decompose()

    # Convert the content to a list of elements and remove the last non-<br> string
    content_list = list(content_div.children)
    for element in reversed(content_list):
        if not (element.name == 'br' or isinstance(element, str) and element.strip() == ''):
            if isinstance(element, str):
                element.extract()
            break

    # Get the cleaned HTML content of the element
    cleaned_content = content_div.decode_contents()

    return cleaned_content


if __name__ == '__main__':
    url = 'https://www.bqghh.cc/book/12517/1.html'
    content = get_chapter_content(url)
    print(content)
