from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards import marketplace_keyboard

start_router = Router()


# ==============
# Command /start
# ==============
@start_router.message(CommandStart())
async def program_start(message: types.Message):
    user = message.from_user.first_name
    hello_text = (
        f"👋 Привет, *{user}!* \n\n"
        "Ты в **Products Insider** 🛍️ — месте, где товары говорят сами за себя!\n\n"
        "Здесь можно:\n"
        "📦 Искать товары по категориям\n"
        "💸 Сравнивать цены и находить выгодные предложения\n"
        "⭐ Смотреть рейтинги и отзывы покупателей\n"
        "🔔 Следить за новыми скидками\n\n"
        "Выбери маркетплейс, с которого начнем поиск 🔽\n\n"
        "ℹ️ Введи /help, чтобы узнать все доступные команды."
    )
    await message.answer(hello_text, parse_mode="Markdown", reply_markup=marketplace_keyboard())


# ==============
# Button "Start"
# ==============
@start_router.callback_query(lambda c: c.data == "start_bot")
async def start_button(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()

    user = callback.from_user.first_name
    hello_text = (
        f"👋 Привет, *{user}!* \n\n"
        "Ты в **Products Insider** 🛍️ — месте, где товары говорят сами за себя!\n\n"
        "Здесь можно:\n"
        "📦 Искать товары по категориям\n"
        "💸 Сравнивать цены и находить выгодные предложения\n"
        "⭐ Смотреть рейтинги и отзывы покупателей\n"
        "🔔 Следить за новыми скидками\n\n"
        "Выбери маркетплейс, с которого начнем поиск 🔽\n\n"
        "ℹ️ Введи /help, чтобы узнать все доступные команды."
    )
    await callback.message.answer(hello_text, parse_mode="Markdown", reply_markup=marketplace_keyboard())
    await callback.answer()