from aiogram import Router, types
from aiogram.filters import Command
from keyboards import (
    uzum_categories_keyboard,
    uzum_products_keyboard,
    product_details_keyboard,
    yandex_categories_keyboard,
    yandex_products_keyboard,
    uzum_top_selling_keyboard
    )
from scrapers import (
    get_uzum_categories, 
    get_uzum_products, 
    get_uzum_top_selling,
    get_yandex_categories,
    get_yandex_products
    )
from .start import program_start
from selenium.common.exceptions import TimeoutException
import hashlib

market_router = Router()

# ==============================
# Constants
# ==============================
PAGE_SIZE = 6  
PRODUCTS_PAGE_SIZE = 6  

# ==============================
# Caches for users
# ==============================
categories_cache = {} 
products_cache = {}   


# ==============================
# Command /uzum
# ==============================
@market_router.message(Command("uzum"))
async def market_uzum(message: types.Message):
    chat_id = message.chat.id
    loading_msg = await message.answer("Обновляем категории... ⏳")
    
    try:
        categories = get_uzum_categories("https://uzum.uz/ru")
        categories_cache[chat_id] = categories
        await loading_msg.delete()
    except TimeoutException:
        await loading_msg.delete()
        await message.answer("Не удалось загрузить категории 😢 Попробуйте позже.")
        return

    text = (
        "🛍 Добро пожаловать в 🍇 **Uzum Market**!\n\n"
        "Выберите категорию, чтобы начать поиск товаров. ⬇️\n\n"
        "💡 Подсказка: используйте кнопки для навигации — это быстрее и удобнее!"
    )

    await message.answer(
        text,
        reply_markup=uzum_categories_keyboard(categories, page=0),
        parse_mode="Markdown"
    )


# ==============================
# Category pagination
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


# =======================================
# Category selection and showing products
# =======================================
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

    products_cache[chat_id] = products

    await callback.message.edit_text(
        f"🛒 Товары категории **{category['title'].replace('.', '\\.')}**\\. Выберите товар ⬇️",
        parse_mode="MarkdownV2",
        reply_markup=uzum_products_keyboard(products, page=0, category_url = category['url'].replace("https://uzum.uz/ru/category/", ""))
    )


# ==============================
# Products pagintaion
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

    text = "🛒 Товары категории:\n\n"

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=uzum_products_keyboard(products, page)
    )


@market_router.callback_query(lambda c: c.data.startswith("top_"))
async def top_selling_uzum(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    category_link = callback.data.replace("top_", "")

    # Уведомляем пользователя
    loading_msg = await callback.message.answer("⏳ Загружаем самые продаваемые товары с Uzum...")

    try:
        # Запуск парсера
        products = get_uzum_top_selling(f"https://uzum.uz/ru/category/{category_link}")
    except Exception as e:
        await loading_msg.delete()
        await callback.message.answer(f"❌ Ошибка при получении товаров: {e}")
        return

    await loading_msg.delete()

    # Проверяем результат
    if not products:
        await callback.message.answer("😢 Не удалось найти топ-продаваемые товары.")
        return

    # Формируем ответ (до 10 товаров)
    text = "🔥 **Топ-продаваемые товары Uzum:**\n\n"
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=uzum_top_selling_keyboard(products, page=0))    

# ===========================
# Button "Back to categories"
# ===========================
@market_router.callback_query(lambda c: c.data.startswith("back_to_categories"))
async def back_to_categories(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    await callback.answer()
    await market_uzum(callback.message)


# ===============
# Product Details
# ===============
@market_router.callback_query(lambda c: c.data.startswith("product_"))
async def product_detail_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer("Товары пока не загружены 😢")
        return

    index = int(callback.data.split("_")[-1])
    if index >= len(products):
        await callback.message.answer("Товар не найден 😢")
        return

    product = products[index]
    text = (
        f"✨🛍 **{product['title']}** ✨\n\n"
        f"💰 Цена: **{product['price']} сум**\n"
        f"📅 Рассрочка: *{product['price_per_month']}* в месяц\n"
        f"🔗 [Открыть в Uzum]({product['url']})"
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=product_details_keyboard(product))

@market_router.callback_query(lambda c: c.data.startswith("yandex_product_"))
async def yandex_product_detail_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer("Товары пока не загружены 😢")
        return

    index = int(callback.data.split("_")[-1])
    if index >= len(products):
        await callback.message.answer("Товар не найден 😢")
        return

    product = products[index]
    text = (
        f"✨🛍 **{product['title']}** ✨\n\n"
        f"💰 Цена: **{product['price']} сум**\n"
        f"📅 Оценка : *{product['rating']}*\n"
        f"🔗 [Открыть в Yandex]({product['url']})"
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=product_details_keyboard(product))


# =========================
# Button "Back to products"
# =========================
@market_router.callback_query(lambda c: c.data.startswith("back_to_products"))
async def back_to_products(callback: types.CallbackQuery):
    if callback.message:
        await callback.message.delete()
    await callback.answer()


# ==============================
# Command /yandex
# ==============================
@market_router.message(Command("yandex"))
async def market_yandex(message: types.Message):
    chat_id = message.chat.id
    loading_msg = await message.answer("Обновляем категории... ⏳")

    try:
        categories = get_yandex_categories("https://market.yandex.uz/")
        categories_cache[chat_id] = categories
        await loading_msg.delete()
    except TimeoutException:
        await loading_msg.delete()
        await message.answer("Категории пока не загружены 😢\nНажмите /yandex чтобы обновить.")
        return

    text = (
        "🛍 Добро пожаловать в 🟨 **Yandex Market**!\n\n"
        "Выберите категорию, чтобы начать поиск товаров. ⬇️\n\n"
        "💡 Подсказка: используйте кнопки для навигации — это быстрее и удобнее!"
    )

    await message.answer(
        text,
        reply_markup=yandex_categories_keyboard(categories, page=0),
        parse_mode="Markdown"
    )


@market_router.callback_query(lambda c: c.data.startswith("yandex_page_"))
async def yandex_categories_pagination(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    page = int(callback.data.split("_")[-1])

    categories = categories_cache.get(chat_id)
    if not categories:
        await callback.message.edit_text(
            "Категории пока не загружены 😢\nНажмите /yandex чтобы обновить."
        )
        return

    await callback.message.edit_text(
        "🛍 Выберите категорию ⬇️",
        parse_mode="Markdown",
        reply_markup=yandex_categories_keyboard(categories, page)
    )


# =======================================
# Category selection and showing products
# =======================================
@market_router.callback_query(lambda c: c.data.startswith("yandex_") and not c.data.startswith(("yandex_product_", "yandex_products_page_")))
async def yandex_category_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    category_hash = callback.data.split("_")[-1]
    categories = categories_cache.get(chat_id, [])
    category = next(
        (c for c in categories if hashlib.md5(c["title"].encode()).hexdigest()[:8] == category_hash),
        None
    )

    if not category:
        await callback.message.answer("❌ Не удалось найти категорию.")
        return

    loading_msg = await callback.message.answer(f"⏳ Загружаем товары категории **{category['title']}...**", parse_mode="Markdown",)
    products = get_yandex_products(category["url"])
    await loading_msg.delete()

    if not products:
        await callback.message.answer("Пока нет товаров в этой категории 😢")
        return

    products_cache[chat_id] = products

    await callback.message.edit_text(
        f"🛒 Товары категории **{category['title'].replace('.', '\\.')}**\\. Выберите товар ⬇️",
        parse_mode="MarkdownV2",
        reply_markup=yandex_products_keyboard(products, page=0)
    )


@market_router.callback_query(lambda c: c.data.startswith("yandex_products_page_"))
async def yandex_products_pagination(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    page = int(callback.data.split("_")[-1])

    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer("Товары пока не загружены 😢")
        return

    text = "🛒 Товары категории:\n\n"

    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=yandex_products_keyboard(products, page)
    )


# ==============================
# Choosing marketplace
# ==============================
@market_router.callback_query(lambda c: c.data.startswith("market_"))
async def callback_market(callback: types.CallbackQuery):
    await callback.answer()
    if callback.message:
        await callback.message.delete()

    if callback.data == "market_uzum":
        await market_uzum(callback.message)
    elif callback.data == "market_yandex":
        await market_yandex(callback.message)


# ==============================
# Button "Back"
# ==============================
@market_router.callback_query(lambda c: c.data == "back_home")
async def callback_back_home(callback: types.CallbackQuery):
    await callback.answer()
    await program_start(callback.message)
