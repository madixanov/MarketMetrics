from aiogram import Dispatcher, Bot
from config import BOT_TOKEN
from handlers import start_router, help_router, market_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scrapers.update_price import update_prices
import logging
import asyncio
from pytz import timezone

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    # -------- Планировщик --------
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_prices, "cron", hour=5, minute=0, timezone=timezone("Asia/Tashkent"))
    scheduler.start()

    print("📅 Задачи планировщика:")
    for job in scheduler.get_jobs():
        print("  -", job)

    # ------- Подключаем роутеры -------
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(market_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot is stopped")