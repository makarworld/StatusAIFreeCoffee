# @StatusAIEnergyBot

import re
from sys import stderr

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from dotenv import dotenv_values
from loguru import logger
from peewee import BooleanField, CharField, IntegerField, Model
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
    user_id = IntegerField(unique=True)
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


@dp.message(F.chat.type == "private")
async def start(message: Message):
    try:
        logger.info(
            f"User: @{message.from_user.username} |  ID: {message.from_user.id} | Text: {message.text}"
        )

        user, _ = User.get_or_create(user_id = message.from_user.id)
        user: User 

        user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
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
                f"Status Code: {status_code} | Response Body: {str(response_body)[12:]}"
            )
            await message.answer(
                "<b>❤️ Успешно отправил вам кофе</b>\n\n<b>❤️ Successfully sent you coffee</b>"
            )
        else:
            await message.answer(
                "<b>😈 Отправь мне свой инвайт-код:</b>\n\n<b>😈 Send me your invite code:</b>"
            )

    except Exception as e:
        logger.exception(f"Error: {e}")


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
