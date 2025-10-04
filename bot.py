from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from handlers import start_router, help_router, market_router
import logging
import asyncio


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main():
    # ------- Connecting route -------
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(market_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    # -------- Showing logs in Terminal --------
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is stopped")