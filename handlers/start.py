from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards import marketplace_keyboard
from texts import message_texts as mt

start_router = Router()


# ==============
# Command /start
# ==============
@start_router.message(CommandStart())
async def program_start(message: types.Message):
    user = message.from_user.first_name
    await message.answer(mt.TEXTS['start_message'].format(user=user), parse_mode="Markdown", reply_markup=marketplace_keyboard())


# ==============
# Button "Start"
# ==============
@start_router.callback_query(lambda c: c.data == "start_bot")
async def start_button(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    user = callback.from_user.first_name
    await callback.message.answer(mt.TEXTS['start_message'].format(user=user), parse_mode="Markdown", reply_markup=marketplace_keyboard())
    await callback.answer()