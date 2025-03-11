# @StatusAIEnergyBot

import asyncio
import re
from sys import stderr
import time

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters.command import Command
from dotenv import dotenv_values
from loguru import logger
from peewee import BooleanField, CharField, BigIntegerField, Model
from playhouse.postgres_ext import PostgresqlExtDatabase

from refer import async_login_with_invite_code

config = dotenv_values(".env")
DB_NAME = config.get("DB_NAME", "postgres")
DB_USER = config.get("DB_USER", "postgres")
DB_PASS = config.get("DB_PASS", "postgres")
DB_HOST = config.get("DB_HOST", "postgres")
DB_PORT = int(config.get("DB_PORT", "5432"))

db = PostgresqlExtDatabase(
    database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
)

class User(Model):
    user_id = BigIntegerField(unique=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    last_refcode = CharField(null=True)
    is_admin: bool = BooleanField(default=False)

    class Meta:
        database = db


User.create_table(safe=True)

logger.remove()
logger.add(stderr)

logger.add(
    "bot.log",
    backtrace=True,
    diagnose=True,
)

logger.level("DEBUG", color="<magenta>")


PROXY = config.get("PROXY", None)

dp = Dispatcher()

users_last_messages = {}
coffee_count = {}

@dp.message(F.chat.type == "private")
async def start(message: Message):
    try:
        logger.info(
            f"User: @{message.from_user.username} |  ID: {message.from_user.id} | Text: {message.text}"
        )

        user: User = User.get_or_none(user_id = message.from_user.id)
        if not user:
            user = User(
                user_id = message.from_user.id,
                username = message.from_user.username,
                first_name = message.from_user.first_name,
                last_name = message.from_user.last_name,
                is_admin = False
            )
            user.save()

        refcode = re.findall(r"[0-9a-zA-Z]{10}", message.text or "")

        if refcode:
            refcode = refcode[0]
            user.last_refcode = refcode
            user.save()
            
            status_code, response_body = await async_login_with_invite_code(
                refcode, proxy=PROXY
            )
            logger.info(
                f"Status Code: {status_code} | Response Body: {str(response_body)[:12]}"
            )
            # if last message was more than 5 seconds ago, send message
            if time.time() - users_last_messages.get(user.user_id, 0) >= 5:
                count = coffee_count.get(user.user_id, 1)
                await message.answer(
                    f"<b>❤️ Успешно отправил вам {count} кофе</b>\n\n<b>❤️ Successfully sent you {count} coffee</b>"
                )
                users_last_messages[user.user_id] = time.time()
                coffee_count.pop(user.user_id)
            else:
                coffee_count[user.user_id] = (coffee_count.get(user.user_id, 0) + 1)
            
        else:
            await message.answer(
                "<b>😈 Отправь мне свой инвайт-код:</b>\n\n<b>😈 Send me your invite code:</b>"
            )

    except Exception as e:
        logger.exception(f"Error: {e}")

@dp.message(F.chat.type == "private", Command("mailing"))
async def mailing(message: Message):
    user: User = User.get_or_none(user_id = message.from_user.id)
    if not user or not user.is_admin:
        return

    users = User.select()

    message = (
        "<b>Спасибо за использование бота ❤️</b>\n\n"
        "<b>В связи с огромным потоком сообщений бот будет отвечать на них раз в 5 секунд</b>\n"
        "<b>Канал с новостями:</b> @StatusAIFree"
    )

    for user in users:
        try:
            await bot.send_message(user.user_id, message)
            logger.info(f"Sent mailing to {user.user_id}")
        except Exception as e:
            logger.exception(f"Error: {e}")
        
        await asyncio.sleep(0.5)
    
    await message.answer("<b>✅ Отправлено</b>")


if __name__ == "__main__":
    BOT_TOKEN = config.get("BOT_TOKEN")
    # create bot instance
    bot = Bot(token=BOT_TOKEN, disable_web_page_preview=True, parse_mode="HTML")

    async def on_startup(*args, **kwargs):
        me = await bot.get_me()
        logger.success(f"Started as @{me.username}")

    dp.startup.register(on_startup)
    # run
    dp.run_polling(bot)
