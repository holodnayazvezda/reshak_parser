import asyncio
import json

import requests
import urllib3
from bs4 import BeautifulSoup

from config import get_headers, MAIN_URL
from database_worker import write_information_to_database
from image_encoder_and_decoder import encode_image_to_base64
from numbers_utils import numbers_elements_checker, parse_gdz_dict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def parse_book_data(url: str, book_data: dict, db_key: str) -> None:
    try:
        r = requests.get(url, headers=await get_headers(), verify=False)
        if r.status_code == 200:
            print(f'Парсю {db_key}')
            soup = BeautifulSoup(r.text, 'html.parser')
            # получаем article элемент с изображением книги и кнопками номеров
            numbers_article = soup.find('article', class_='lcol')
            # получаем изображение книги и кодируем его в base64
            book_image_img_element = numbers_article.find('div', class_='indexImg').find('div', class_='book').find('img')
            book_image_link = book_image_img_element.get('src')
            if book_image_link is None:
                book_image_link = book_image_img_element.get('data-cfsrc')
            book_image_absolute_link = MAIN_URL + book_image_link
            book_image_base64 = await encode_image_to_base64(book_image_absolute_link)
            # добавляем изображение в словарь данных книги
            book_data['img'] = book_image_base64
            # начинаем парсить кнопки номеров
            # создаем список в котором лежат все html элементы subtitile и razdel (заголовки и блоки с кнопками)
            filtered_numbers_article_html_children = list(
                filter(lambda el: numbers_elements_checker(el, ['subtitle'], ['razdel']), numbers_article.children)
            )
            if len(filtered_numbers_article_html_children) > 0:
                # если в списке есть элементы, то формируем словарь данных номеров
                book_gdz = await parse_gdz_dict(filtered_numbers_article_html_children, 'subtitle', db_key)
            else:
                # если в списке нет элементов, значит страница решебника имеет другой формат и парсим несколько по-другому
                menu_ul = numbers_article.find('ul', attrs={'id': 'slidemenu', 'class': 'reset-index'})
                numbers_blocks_titles = menu_ul.find_all('span', class_='sublnk')
                numbers_blocks_divs = menu_ul.find_all('div', class_='sublnk1')
                book_gdz = {}
                for title, block in zip(numbers_blocks_titles, numbers_blocks_divs):
                    title_text = title.text.strip()
                    filtered_block_html_children = list(
                        filter(lambda el: numbers_elements_checker(el, ['partName'], ['partContent']), block.children)
                    )
                    # на основании новых полученных элементов формируем словарь данных для одного вложенного блока
                    block_gdz = await parse_gdz_dict(filtered_block_html_children, 'partName', db_key)
                    book_gdz[title_text] = block_gdz
            book_data['gdz'] = book_gdz
            await write_information_to_database('gdz.sqlite3', 'books_data', json.dumps(book_data), db_key)
            print(f'Спарсил {db_key}')
        elif r.status_code != 404:
            print(f'Ошибка {r.status_code}! Пытаюсь еще раз {url}')
            await asyncio.sleep(0.3)
            await parse_book_data(url, book_data, db_key)
    except Exception as e:
        print(f'Ошибка парсинга: {e} {url}')
        await asyncio.sleep(0.3)
        await parse_book_data(url, book_data, db_key)


if __name__ == '__main__':
    import time
    start_time = time.time()
    asyncio.run(
        parse_book_data(
            'https://reshak.ru/reshebniki/algebra/9/kolyagin/index.html',
            {}, 'book_data')
    )
    print(f'Time: {time.time() - start_time}')
