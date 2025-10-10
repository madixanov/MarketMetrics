from aiogram import Router, types
from  aiogram.filters import Command
from keyboards import start_keyboard
from texts import message_texts as mt

help_router = Router()

# =============
# Command /help
# =============
@help_router.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(mt.TEXTS['help_message'], parse_mode="Markdown", reply_markup=start_keyboard())