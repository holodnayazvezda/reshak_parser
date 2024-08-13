import asyncio
from threading import Thread

import requests
import urllib3
from bs4 import BeautifulSoup

from async_thread_runner import start
from authors_and_books import parse_authors_and_books
from config import *
from database_worker import write_information_to_database

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def parse_classes_and_subjects() -> None:
    try:
        r = requests.get(MAIN_URL, headers=await get_headers(), verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            classes_block = soup.find('ul', class_='nav-class flexbox')
            # выбираем все li верхнего уровня и удаляем последний элемент (потому что он не про класс, а про ЕГЭ).
            classes_lis = list(filter(lambda el: str(el).strip(), classes_block.children))[:-1]
            for class_li in classes_lis:
                # получаем название класса
                class_a = class_li.find('a')
                class_name = class_a.text.strip()
                await write_information_to_database("gdz.sqlite3", 'classes', class_name)
                # получаем имеющиеся предметы для класса
                class_subjects_ul = class_li.find('ul', class_='nav-subject')
                class_subjects_lis = list(filter(lambda el: str(el).strip(), class_subjects_ul.children))
                for class_subject_li in class_subjects_lis:
                    # получаем html тэг, где хранится ссылка на предмет
                    class_subject_a = class_subject_li.find('a')
                    # получаем название предмета и ссылку на предмет
                    class_subject_name = class_subject_a.text.strip()
                    class_subject_url = MAIN_URL + class_subject_a.get('href').strip()
                    await parse_authors_and_books(class_subject_url, f'{class_name}-{class_subject_name}')
                    await write_information_to_database('gdz.sqlite3', 'subjects', class_subject_name, class_name)
        else:
            print('Ошибка! Не удалось спарсить классы!')
    except Exception as e:
        print(f'Ошибка! Не удалось спарсить классы! {e}')


if __name__ == '__main__':
    asyncio.run(parse_classes_and_subjects())
