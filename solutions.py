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
            divs_with_classes = list(filter(lambda el: el.attrs.get('class'), solution_article.find_all('div')))
            images_blocks_in_solution = list(filter(lambda el: 'pic_otvet1' in el.attrs.get('class')[0], divs_with_classes))
            if images_blocks_in_solution:
                images = list(map(lambda el: el.find('img'), images_blocks_in_solution))
                solution_images_links = []
                for image in images:
                    image_link = image.get('src')
                    if image_link is None:
                        image_link = image.get('data-cfsrc')
                        if image_link is None:
                            image_link = image.get('data-src')
                    if image_link != '/pic/zapret_pravo.png':
                        solution_images_links.append(MAIN_URL + image_link)
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
                except Exception:
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
    asyncio.run(parse_solutions('https://reshak.ru/otvet/otvet_txt.php?otvet1=/spotlight9/images/module2/c/2', db_key=''))
    print(f'Time: {time.time() - start_time}')
    