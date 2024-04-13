import asyncio
import apykuma
import logging

from aiogram import Bot, Dispatcher
from src.config import TOKEN, KUMA_TOKEN
from src.handlers import telegram


async def start_bot():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(telegram.router)
    if KUMA_TOKEN != "":
        await apykuma.start(url=KUMA_TOKEN, delay=10)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
