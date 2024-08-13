import asyncio

import requests
import urllib3
from bs4 import BeautifulSoup
from rich import json

from config import get_headers, MAIN_URL
from database_worker import write_information_to_database

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def parse_solutions(url: str, db_key: str):
    try:
        r = requests.get(url, headers=await get_headers(), verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            solution_article = soup.find('article', class_='lcol')
            is_image_in_solution = soup.find('div', class_='pic_otvet1') is not None
            if is_image_in_solution:
                images = solution_article.find_all('img')
                solution_images_links = []
                for image in images:
                    image_link = image.get('src')
                    if image_link is None:
                        image_link = image.get('data-cfsrc')
                        if image_link is None:
                            image_link = image.get('data-src')
                    if image_link != '/pic/zapret_pravo.png':
                        solution_images_links.append(MAIN_URL + image_link)
                amount_of_solutions = solution_article.find_all('h2', class_='titleh2')
                solution_images_links = solution_images_links[:len(amount_of_solutions)]
                solution_data = {
                    'url': url,
                    'type': 'img',
                    'img_links': solution_images_links
                }
            else:
                try:
                    text_solution_main_div = solution_article.find('div', class_='mainInfo')
                    solution_text = text_solution_main_div.get_text(strip=True, separator='\n')
                    solution_data = {
                        'url': url,
                        'type': 'text',
                        'text': solution_text
                    }
                except Exception as e:
                    solution_data = {
                        'url': url,
                        'type': 'url'
                    }
            await write_information_to_database('gdz.sqlite3', 'solutions', json.dumps(solution_data), db_key)
        elif r.status_code != 404:
            print(f'Ошибка {r.status_code}! Пытаюсь еще раз {url}')
            await asyncio.sleep(0.3)
            await parse_solutions(url, db_key)
    except Exception as e:
        print(f'Ошибка парсинга: {e} {url}')
        await asyncio.sleep(0.3)
        await parse_solutions(url, db_key)


if __name__ == '__main__':
    import time
    start_time = time.time()
    asyncio.run(parse_solutions('https://reshak.ru/otvet/reshebniki.php?otvet=pract3&predmet=bogolubov9', db_key=''))
    print(f'Time: {time.time() - start_time}')
    