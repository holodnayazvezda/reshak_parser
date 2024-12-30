import random

MAIN_URL = 'https://reshak.ru'

ua = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
    'Opera/9.80 (Macintosh; Intel Mac OS X; U; en) Presto/2.2.15 Version/10.00'
]


async def get_headers():
    return {
        'User-Agent': random.choice(ua),
        'Host': 'reshak.ru',
        'Accept': '*/*',
    }
