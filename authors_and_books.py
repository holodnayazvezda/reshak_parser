import asyncio
from threading import Thread

import requests
import urllib3
from bs4 import BeautifulSoup

from async_thread_runner import start
from book_numbers import parse_book_data
from config import get_headers, MAIN_URL
from database_worker import write_information_to_database

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def parse_authors_and_books(url: str, db_key: str) -> None:
    try:
        r = requests.get(url, headers=await get_headers(), verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            gdz_div = soup.find('div', class_='main_gdz list_gdz flexbox')
            # найти в gdz_div все article с классом main_gdz-div, у которых поле style является пустым ("")
            books_articles = gdz_div.find_all('article', class_='main_gdz-div')
            # cловарь для храннеия авторов и их книг (в случае, если их несколько)
            dict_of_authors_and_books = {}
            for article in books_articles:
                book_a = article.find('a')
                # проверить есть ли у названия книги дополнительные слова (по типу углубленный)
                book_year = ''
                book_year_div = book_a.find('div', class_='bookYear')
                if book_year_div is not None:
                    book_year = book_year_div.text.strip()
                # получить ссылку на учебник
                link = MAIN_URL + book_a['href']
                # получить авторов учебника
                authors_string = book_a.find('div', class_='author').text.strip()
                authors_list = authors_string.split(', ')
                book_leading_author = authors_list[0]
                # получить название учебника
                book_name = book_a.get('alt')
                book_name_cropped = book_name.replace('ГДЗ ', '')
                book_full_name = f'{book_name_cropped} {book_year}'.strip()
                # создать новый db_key для таблицы books
                new_db_key = f'{db_key}-{book_leading_author}'
                if book_leading_author in dict_of_authors_and_books:
                    dict_of_authors_and_books[book_leading_author].append(book_full_name)  # добавить книгу в словарь
                else:
                    dict_of_authors_and_books[book_leading_author] = [book_full_name]  # создать новый ключ в словаре
                    await write_information_to_database('gdz.sqlite3', 'authors', book_leading_author, db_key)
                await write_information_to_database('gdz.sqlite3', 'books', book_full_name, new_db_key)
                # начинаем формировать словарь данных книги, до конца он будет сформирован в book_numbers.py #
                book_data = {
                    'name': book_full_name,
                    'authors': authors_string
                }
                Thread(target=start, args=(parse_book_data, [link, book_data, f'{new_db_key}-{book_full_name}'])).start()
        elif r.status_code != 404:
            print(f'Ошибка {r.status_code}! Пытаюсь еще раз {url}')
            await asyncio.sleep(0.3)
            await parse_authors_and_books(url, db_key)
    except Exception as e:
        print(f'Ошибка парсинга: {e} {url}')
        await asyncio.sleep(0.3)
        await parse_authors_and_books(url, db_key)


if __name__ == '__main__':
    asyncio.run(parse_authors_and_books('https://reshak.ru/tag/9klass_alg.html', ''))
