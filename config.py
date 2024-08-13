from fake_useragent import UserAgent

MAIN_URL = 'https://reshak.ru'

ua = UserAgent(browsers=["chrome", "firefox", "safari"])


async def get_headers():
    return {
        'User-Agent': ua.random,
        'Host': 'reshak.ru',
        'Accept': '*/*',
    }
