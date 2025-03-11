# @StatusAIEnergyBot

import re
from sys import stderr

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import dotenv_values
from loguru import logger

from refer import async_login_with_invite_code

logger.remove()
logger.add(stderr)

logger.add(
    "bot.log",
    backtrace=True,
    diagnose=True,
)

logger.level("DEBUG", color="<magenta>")


config = dotenv_values(".env")

dp = Dispatcher()


@dp.message()
async def start(message: Message):
    try:
        logger.info(
            f"User: @{message.from_user.username} |  ID: {message.from_user.id} | Text: {message.text}"
        )

        refcode = re.findall(r"[0-9a-zA-Z]{10}", message.text or "")

        if refcode:
            refcode = refcode[0]
            status_code, response_body = await async_login_with_invite_code(refcode)
            logger.info(f"Status Code: {status_code} | Response Body: {response_body}")
            await message.answer(
                "❤️ Успешно отправил вам кофе <3\n\n❤️ Successfully sent you coffee <3"
            )
        else:
            await message.answer(
                "😈 Отправь мне свой инвайт-код:\n\n😈 Send me your invite code:"
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
