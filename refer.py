import random
import re
import time
from hashlib import md5
from sys import stderr

from curl_cffi import requests
from loguru import logger

logger.remove()
logger.add(stderr)

logger.add(
    "bot.log",
    backtrace=True,
    diagnose=True,
)

logger.level("DEBUG", color="<magenta>")


apk_cache: list = None


async def get_apk_version() -> tuple[str, str]:
    global apk_cache

    build_pattern = r">\((\d{2})\)<\/span>"
    version_pattern = r"status - sims but social media (\d+\.\d+\.\d+)"

    if apk_cache is not None:
        if time.time() - apk_cache[2] < 10 * 60:  # 10 min
            return apk_cache[:2]

    async with requests.AsyncSession() as session:
        response = await session.get(
            "https://apkcombo.app/downloader/?package=link.socialai.app&ajax=1"
        )
        print(response.text)

        build = re.search(build_pattern, response.text).group(1)
        version = re.search(version_pattern, response.text).group(1)

        apk_cache = [build, version, time.time()]

        logger.success(
            f"Updated APK cache from apkcombo | Build: {build} | Version: {version}"
        )
        return apk_cache[:2]


def sync_get_apk_version() -> tuple[str, str]:
    global apk_cache

    build_pattern = r">\((\d{2})\)<\/span>"
    version_pattern = r"status - sims but social media (\d+\.\d+\.\d+)"

    if apk_cache is not None:
        if time.time() - apk_cache[2] < 10 * 60:  # 10 min
            return apk_cache[:2]

    response = requests.get(
        "https://apkcombo.app/downloader/?package=link.socialai.app&ajax=1"
    )

    build = re.search(build_pattern, response.text).group(1)
    version = re.search(version_pattern, response.text).group(1)

    apk_cache = [build, version, time.time()]

    logger.success(
        f"Updated APK cache from apkcombo | Build: {build} | Version: {version}"
    )
    return apk_cache[:2]


def login_with_invite_code(invite_code: str):
    random_user_id = random.randint(100000000000000000000, 100999999999999999999)
    device_id = f"md5/{md5(str(random_user_id).encode()).hexdigest()}"

    build, version = sync_get_apk_version()
    # Определяем URL
    url = "https://social-ai-prod.uc.r.appspot.com/user/auth/login"
    # Определяем заголовки
    headers = {
        "accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "app": "SOCIALAI",
        "build": build,
        "Connection": "Keep-Alive",
        "device-id": device_id,
        "Host": "social-ai-prod.uc.r.appspot.com",
        "User-Agent": "okhttp/4.12.0",
        "version": version,
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

    build, version = await get_apk_version()

    # Определяем URL
    url = "https://social-ai-prod.uc.r.appspot.com/user/auth/login"
    # Определяем заголовки
    headers = {
        "accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip",
        "app": "SOCIALAI",
        "build": build,
        "Connection": "Keep-Alive",
        "device-id": device_id,
        "Host": "social-ai-prod.uc.r.appspot.com",
        "User-Agent": "okhttp/4.12.0",
        "version": version,
    }

    # Определяем данные формы
    data = {
        "timezone": "Europe/Moscow",
        "inviteCode": invite_code,
        "googleUserId": random_user_id,
    }

    # Отправляем PUT-запрос
    async with requests.AsyncSession(proxy=proxy) as session:
        response = await session.put(url, headers=headers, data=data)
    print(response.text)
    # Возвращаем статус-код и тело ответа
    return response.status_code, response.json()


if __name__ == "__main__":
    # Пример использования функции
    invite_code = ""  # Замените на нужный код приглашения
    status_code, response_body = login_with_invite_code(invite_code)

    print("Status Code:", status_code)
    print("Response Body:", response_body)
