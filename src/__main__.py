import asyncio
import apykuma

from aiogram import Bot, Dispatcher
from src.config import TOKEN, KUMA_TOKEN
from src.handlers import telegram


async def start_bot():
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    dp.include_router(telegram.router)
    if KUMA_TOKEN != "":
        await apykuma.start(url=KUMA_TOKEN, delay=10)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
