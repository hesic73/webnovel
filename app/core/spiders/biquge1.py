"""
https://www.xbiqugew.com  
"""

import logging
import requests
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def search_book(book_name: str, biquge_url: str) -> str:
    search_url_base = urljoin(biquge_url, "/modules/article/search.php")
    query_params = {'searchkey': book_name.encode('GBK')}
    query_string = urlencode(query_params, encoding='GBK')
    search_url = f"{search_url_base}?{query_string}"

    novel_source = requests.get(search_url).text
    soup = BeautifulSoup(novel_source, 'html.parser')

    novels_div = soup.find('div', class_='novelslistss')
    if novels_div is None:
        raise Exception('No novels found')

    results = novels_div.find_all('li')
    for result in results:
        novel_name_span = result.find('span', class_='s2')
        novel_author_span = result.find('span', class_='s4')

        novel_url = novel_name_span.find('a')['href']
        novel_name = novel_name_span.find('a').text
        novel_author = novel_author_span.text

        if novel_name == book_name:

            logger.info(f'Found novel:{novel_name} author:{novel_author}')
            return novel_url

    raise Exception('No novels found')


def get_novel_data(url: str):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    info = soup.find('div', id='info')

    novel_name = info.find('h1').text
    author_name = info.find('p').find('a').text
    intro = soup.find('div', id='intro').text

    chapters_list = soup.find('div', id='list').find('dl')

    center_element = chapters_list.find_all('center')[0]

    dd_elements_after_center = [
        siblings for siblings in center_element.find_next_siblings() if siblings.name == 'dd']

    chapters = [(dd.text, urljoin(url, a['href']))
                for dd in dd_elements_after_center if (a := dd.find('a'))]

    return {
        'title': novel_name,
        'author': author_name,
        'intro': intro,
        'chapters': chapters
    }


def get_chapter_content(url: str):
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'html.parser')

    content_div = soup.find('div', id='content')

    # Get the raw HTML content of the element
    raw_content = content_div.decode_contents()

    # Split the raw content by <br/> to handle the first part separately
    parts = raw_content.split('<br/><br/>', 1)

    # Check if the first part contains "biquge" and remove it
    if len(parts) > 1 and '笔趣阁' in parts[0]:
        raw_content = parts[1]
    else:
        raw_content = ''.join(parts)

    return raw_content
