"""
https://www.piaotia.com/
"""


import requests
from urllib.parse import urljoin, urlencode

from bs4 import BeautifulSoup, NavigableString


def get_novel_data(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    response = requests.get(url, headers=headers)
    html = response.content.decode('gbk')
    soup = BeautifulSoup(html, 'html.parser')

    novel_name: str = soup.find('div', class_='title').find('h1').text
    novel_name = novel_name.replace('最新章节', '')

    div_list = soup.find('div', class_='list')
    author_text = div_list.text
    author_name = author_text.split('：')[1].split()[0]

    intro = ""

    chapters_list = soup.find('div', class_="centent").find_all('li')

    chapters = [(a.text, urljoin(url, a['href']))
                for item in chapters_list if (a := item.find('a'))]

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
    response = requests.get(url, headers=headers)
    html = response.content.decode('gbk', errors='ignore')

    # Normalize line break tags
    html = html.replace('</br>', '<br/>').replace('<br>', '<br/>')

    # Find the script tag and manually insert the required div
    insert_string = '<div id="content" class="fonts_mesne">'
    script_tag_start = '<script language="javascript">GetFont();</script>'
    html = html.replace(script_tag_start, script_tag_start + insert_string, 1)

    soup = BeautifulSoup(html, 'html.parser')

    content_div = soup.find('div', id='content')

    # Extract text while keeping <br> tags
    content_list = []
    for elem in content_div.children:
        if isinstance(elem, NavigableString):
            content_list.append(str(elem))
        elif elem.name == 'br':
            content_list.append('<br>')

    content_text = ''.join(content_list)

    return content_text
