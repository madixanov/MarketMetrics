from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards import marketplace_keyboard

start_router = Router()

@start_router.message(CommandStart())
async def program_start(message: types.Message):
    user = message.from_user.first_name
    hello_text = (
        f"👋 Привет, *{user}*! \n\n"
        "Добро пожаловать в **Products Insider** 🛒✨\n"
        "Здесь вы можете:\n"
        "📂 Просматривать товары по категориям\n"
        "💰 Сравнивать и сортировать товары\n"
        "⭐ Проверять рейтинги и отзывы\n"
        "🔔 Получать уведомления о лучших предложениях!\n\n"
        "🛒 Выберите **маркетплейс**, на котором хотите искать товары.\n\n"
        "Введите `/help`, чтобы увидеть все команды. 🚀"
    )
    await message.answer(hello_text, parse_mode="Markdown", reply_markup=marketplace_keyboard())

@start_router.callback_query(lambda c: c.data == "start_bot")
async def start_button(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    await program_start(callback.message)
    await callback.answer()