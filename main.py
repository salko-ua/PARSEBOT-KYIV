import asyncio, logging, apykuma

from aiogram import Bot, Dispatcher
from config import TOKEN, KUMA_TOKEN
from handlers import telegram


bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher()


async def register_handlers():
    dp.include_router(telegram.router)


async def start_bot():
    await register_handlers()
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot Online")
    if KUMA_TOKEN != "":
        await apykuma.start(url=KUMA_TOKEN, delay=10)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_bot())
