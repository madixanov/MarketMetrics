from aiogram import Router, types
from aiogram.filters import Command
from keyboards import (
    uzum_categories_keyboard,
    yandex_categories_keyboard,
    uzum_products_keyboard,
    uzum_product_details_keyboard
)
from scrapers import get_uzum_categories, get_uzum_products
from .start import program_start
from selenium.common.exceptions import TimeoutException
import hashlib

market_router = Router()

# ==============================
# Константы
# ==============================
PAGE_SIZE = 6  # количество категорий на странице
PRODUCTS_PAGE_SIZE = 6  # количество товаров на странице

# ==============================
# Кэши для пользователей
# ==============================
categories_cache = {}  # {chat_id: categories}
products_cache = {}    # {chat_id: products}


# ==============================
# Команда /uzum
# ==============================
@market_router.message(Command("uzum"))
async def market_uzum(message: types.Message):
    chat_id = message.chat.id
    loading_msg = await message.answer("Обновляем категории... ⏳")
    
    try:
        categories = get_uzum_categories("https://uzum.uz/ru")
        categories_cache[chat_id] = categories  # сохраняем категории в кэш
        await loading_msg.delete()
    except TimeoutException:
        await loading_msg.delete()
        await message.answer("Не удалось загрузить категории 😢 Попробуйте позже.")
        return

    text = (
        "🛍 Добро пожаловать в **Uzum Market**!\n\n"
        "Выберите категорию, чтобы начать поиск товаров. ⬇️\n\n"
        "💡 Подсказка: используйте кнопки для навигации — это быстрее и удобнее!"
    )

    await message.answer(
        text,
        reply_markup=uzum_categories_keyboard(categories, page=0),
        parse_mode="Markdown"
    )


# ==============================
# Пагинация категорий
# ==============================
@market_router.callback_query(lambda c: c.data.startswith("uzum_page_"))
async def uzum_categories_pagination(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    page = int(callback.data.split("_")[-1])
    
    categories = categories_cache.get(chat_id)
    if not categories:
        await callback.message.edit_text(
            "Категории пока не загружены 😢\nНажмите /uzum чтобы обновить."
        )
        return

    await callback.message.edit_text(
        "🛍 Выберите категорию ⬇️",
        parse_mode="Markdown",
        reply_markup=uzum_categories_keyboard(categories, page)
    )


# ==============================
# Выбор категории и загрузка товаров
# ==============================
# ==============================
# Выбор категории и загрузка товаров (кнопки, без текста)
# ==============================
@market_router.callback_query(lambda c: c.data.startswith("uzum_"))
async def uzum_category_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    category_hash = callback.data.split("_")[1]
    categories = categories_cache.get(chat_id, [])
    category = next(
        (c for c in categories if hashlib.md5(c["title"].encode()).hexdigest()[:8] == category_hash),
        None
    )

    if not category:
        await callback.message.answer("❌ Не удалось найти категорию.")
        return

    loading_msg = await callback.message.answer(f"⏳ Загружаем товары категории {category['title']}...")
    products = get_uzum_products(category["url"])
    await loading_msg.delete()

    if not products:
        await callback.message.answer("Пока нет товаров в этой категории 😢")
        return

    # Сохраняем товары в кэш
    products_cache[chat_id] = products

    # Редактируем сообщение: текст небольшой, кнопки — товары
    await callback.message.edit_text(
        f"🛒 Товары категории **{category['title']}**. Выберите товар ⬇️",
        parse_mode="Markdown",
        reply_markup=uzum_products_keyboard(products, page=0)
    )


# ==============================
# Пагинация товаров
# ==============================
@market_router.callback_query(lambda c: c.data.startswith("products_page_"))
async def uzum_products_pagination(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    page = int(callback.data.split("_")[-1])

    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer("Товары пока не загружены 😢")
        return

    start = page * PRODUCTS_PAGE_SIZE
    end = start + PRODUCTS_PAGE_SIZE
    text = "🛒 Товары категории:\n\n"
    for p in products[start:end]:
        text += f"• {p['title']} — {p['price']}\n"

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=uzum_products_keyboard(products, page)
    )

@market_router.callback_query(lambda c: c.data.startswith("back_to_categories"))
async def back_to_categories(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    await callback.answer()
    await market_uzum(callback.message)

@market_router.callback_query(lambda c: c.data.startswith("product_"))
async def product_detail_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer("Товары пока не загружены 😢")
        return

    index = int(callback.data.split("_")[1])
    if index >= len(products):
        await callback.message.answer("Товар не найден 😢")
        return

    product = products[index]
    text = (
        f"✨🛍 **{product['title']}** ✨\n\n"
        f"💰 Цена: **{product['price']}**\n"
        f"📅 Рассрочка: *{product['price_per_month']}* в месяц\n"
        f"🔗 [Открыть в Uzum]({product['url']})"
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=uzum_product_details_keyboard(product))

@market_router.callback_query(lambda c: c.data.startswith("back_to_products"))
async def back_to_products(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    await callback.answer()


# ==============================
# Выбор маркетплейса
# ==============================
@market_router.callback_query(lambda c: c.data.startswith("market_"))
async def callback_market(callback: types.CallbackQuery):
    await callback.answer()
    if callback.message:
        await callback.message.delete()

    if callback.data == "market_uzum":
        await market_uzum(callback.message)
    elif callback.data == "market_yandex":
        await callback.message.answer(
            "🟨 Yandex Market пока находится в разработке 🛠️\n\n"
            "Скоро вы сможете просматривать категории и находить лучшие товары здесь! 🔜✨",
            reply_markup=yandex_categories_keyboard()
        )


# ==============================
# Кнопка "Назад" в главное меню
# ==============================
@market_router.callback_query(lambda c: c.data == "back_home")
async def callback_back_home(callback: types.CallbackQuery):
    await callback.answer()
    await program_start(callback.message)
