from math import ceil
from threading import Thread

from async_thread_runner import start
from solutions import parse_solutions
from config import MAIN_URL

from datetime import datetime as dt


def numbers_elements_checker(numbers_element, *classes) -> bool:
    return (
            str(numbers_element).strip() not in ['\n', ''] and
            numbers_element.attrs.get('class') is not None
            and numbers_element.attrs.get('class') in classes
    )


async def parse_numbers_data(number_a_elements: list, db_key: str) -> dict:
    numbers_data = {}
    for numbers_a_element in number_a_elements:
        number_link = numbers_a_element.get('href')
        if number_link is not None:
            number_absolute_link = MAIN_URL + number_link
            unique_db_key = db_key + '-' + dt.now().strftime("%Y%m%d%H%M%S%f")
            numbers_data[numbers_a_element.text.strip()] = unique_db_key
            await parse_solutions(number_absolute_link, unique_db_key)
    return numbers_data

    
# группирует словарь с данными номеров вида:
# {'1': 'ссылка', ...} в словарь {'1-98': {'1': 'ссылка', ...,  '98': 'ссылка'}, '99-197': {...}, ...}
async def group_numbers(numbers) -> dict:
    if not isinstance(numbers, dict):
        return numbers
    grouped_numbers = {}
    amount_of_buttons = ceil(len(numbers) / 98)
    keys = list(numbers.keys())
    for i in range(amount_of_buttons):
        pre_main_dict = {}
        count = 0
        for number in keys:
            count += 1
            if count <= 98:
                pre_main_dict[number] = numbers[number]
            else:
                keys = keys[count - 1:]
                break
        title = list(pre_main_dict.keys())[0] + '-' + list(pre_main_dict.keys())[-1]
        grouped_numbers[title] = pre_main_dict
    if len(grouped_numbers) == 1:
        return numbers
    return grouped_numbers


# создает словарь с данными гдз для блоков кнопок
async def parse_gdz_dict(filtered_html_children: list, subtitle_class: str, db_key: str) -> dict:
    gdz = {}
    current_subtitle = None
    for el in filtered_html_children:
        if el.attrs.get('class') == [subtitle_class]:
            # если текущий элемент - это заголовок
            subtitle_text = el.text.strip()
            current_subtitle = subtitle_text
            gdz[subtitle_text] = {}
        else:
            # если текущий элемент - это блок кнопок
            number_a_elements = el.find_all('a')
            # получаем словарь вида: {'1': 'ссылка', ...}
            numbers = await parse_numbers_data(number_a_elements, db_key)
            # при помощи специальной функции группируем словарь с данными номеров
            # группируется на блоки в каждом не более 98 кнопок
            grouped_numbers = await group_numbers(numbers)
            if current_subtitle is not None:
                gdz[current_subtitle].update(grouped_numbers)
            else:
                # если подзаголовок не был найден, то или создаем свой на основе данных номеров
                if len(grouped_numbers) > 1:
                    numbers_block_key = f'{list(grouped_numbers.keys())[0]}-{list(grouped_numbers.keys())[-1]}'
                    gdz[numbers_block_key] = grouped_numbers
                else:
                    # или, если у нас только одна кнопка, то сразу добавляем ее к общему словарю
                    gdz.update(grouped_numbers)
    filtered_gdz = {}
    for key in gdz:
        if gdz[key]: filtered_gdz[key] = gdz[key]
    return filtered_gdz

