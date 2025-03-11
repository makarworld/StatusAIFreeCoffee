import random
from hashlib import md5

from curl_cffi import requests


def login_with_invite_code(invite_code: str):
    random_user_id = random.randint(100000000000000000000, 100999999999999999999)
    device_id = f"md5/{md5(str(random_user_id).encode()).hexdigest()}"

    # Определяем URL
    url = "https://social-ai-prod.uc.r.appspot.com/user/auth/login"
    # Определяем заголовки
    headers = {
        "accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "app": "SOCIALAI",
        "build": "28",
        "Connection": "Keep-Alive",
        "device-id": device_id,
        "Host": "social-ai-prod.uc.r.appspot.com",
        "User-Agent": "okhttp/4.12.0",
        "version": "1.3.1",
    }

    # Определяем данные формы
    data = {
        "timezone": "Europe/Moscow",
        "inviteCode": invite_code,
        "googleUserId": random_user_id,
    }

    # Отправляем PUT-запрос
    response = requests.put(url, headers=headers, data=data)

    # Возвращаем статус-код и тело ответа
    return response.status_code, response.json()


async def async_login_with_invite_code(invite_code: str, proxy: dict = None):
    random_user_id = random.randint(100000000000000000000, 100999999999999999999)
    device_id = f"md5/{md5(str(random_user_id).encode()).hexdigest()}"

    # Определяем URL
    url = "https://social-ai-prod.uc.r.appspot.com/user/auth/login"
    # Определяем заголовки
    headers = {
        "accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "app": "SOCIALAI",
        "build": "28",
        "Connection": "Keep-Alive",
        "device-id": device_id,
        "Host": "social-ai-prod.uc.r.appspot.com",
        "User-Agent": "okhttp/4.12.0",
        "version": "1.3.1",
    }

    # Определяем данные формы
    data = {
        "timezone": "Europe/Moscow",
        "inviteCode": invite_code,
        "googleUserId": random_user_id,
    }

    # Отправляем PUT-запрос
    async with requests.AsyncSession(proxy = proxy) as session:
        response = await session.put(url, headers=headers, data=data)

    # Возвращаем статус-код и тело ответа
    return response.status_code, response.json()


if __name__ == "__main__":
    # Пример использования функции
    invite_code = ""  # Замените на нужный код приглашения
    status_code, response_body = login_with_invite_code(invite_code)

    print("Status Code:", status_code)
    print("Response Body:", response_body)
