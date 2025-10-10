from aiogram import Router, types
from aiogram.filters import Command
from keyboards import *
from scrapers import *
from .start import program_start
from texts import message_texts as mt
from selenium.common.exceptions import TimeoutException
import hashlib
import json

market_router = Router()

# ==============================
# Constants
# ==============================
PAGE_SIZE = 6  
PRODUCTS_PAGE_SIZE = 6  
WATCHLIST_FILE = "watchlist.json"

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
    loading_msg = await message.answer(mt.TEXTS["loading_categories"])
    
    try:
        categories = get_uzum_categories("https://uzum.uz/ru")
        categories_cache[chat_id] = categories
        await loading_msg.delete()
    except TimeoutException:
        await loading_msg.delete()
        await message.answer(mt.TEXTS["no_categories"])
        return

    text = (
        mt.TEXTS["uzum_welcome"]
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
            mt.TEXTS["category_loading_error"]
        )
        return

    await callback.message.edit_text(
        mt.TEXTS["choose_category"],
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
        await callback.message.answer(mt.TEXTS["no_categories"])
        return

    loading_msg = await callback.message.answer(
        f"{mt.TEXTS['loading_products']} {category['title']}...",
        parse_mode="Markdown"
    )
    products = get_uzum_products(category["url"])
    await loading_msg.delete()

    if not products:
        await callback.message.answer(mt.TEXTS["no_products"])
        return

    products_cache[chat_id] = products

    await callback.message.edit_text(
        mt.TEXTS["products"], f"**{category['title'].replace('.', '\\.')}**\\.",
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
        await callback.message.answer(mt.TEXTS["products_load_error"])
        return

    text = mt.TEXTS["products_list"] + "\n\n"

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
    loading_msg = await callback.message.answer(mt.TEXTS["loading_top"])

    try:
        # Запуск парсера
        products = get_uzum_top_selling(f"https://uzum.uz/ru/category/{category_link}")
    except Exception as e:
        await loading_msg.delete()
        await callback.message.answer(mt.TEXTS["error_parsing"], e)
        return

    await loading_msg.delete()

    # Проверяем результат
    if not products:
        await callback.message.answer(mt.TEXTS["no_products"])
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
        await callback.message.answer(mt.TEXTS["no_products"])
        return

    index = int(callback.data.split("_")[-1])
    if index >= len(products):
        await callback.message.answer(mt.TEXTS["no_such_product"])
        return

    product = products[index]
    text = (
        f"✨🛍 **{product['title']}** ✨\n\n"
        f"💰 Цена: **{product['price']} сум**\n"
        f"📅 Рассрочка: *{product['price_per_month']}* в месяц\n"
        f"🔗 [Открыть в Uzum]({product['url']})"
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=product_details_keyboard(product, index))

@market_router.callback_query(lambda c: c.data == "watchlist")
async def view_watchlist(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = str(callback.message.chat.id)

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            watchlist = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        watchlist = {}

    user_watchlist = watchlist.get(chat_id, [])

    if not user_watchlist:
        await callback.message.answer(mt.TEXTS["watchlist_empty"])
        return

    await callback.message.answer(
        mt.TEXTS["watchlist_header"],
        reply_markup=watchlist_keyboard(user_watchlist)
    )


# Просмотр товара
@market_router.callback_query(lambda c: c.data.startswith("view_item:"))
async def view_item(callback: types.CallbackQuery):
    await callback.answer()
    item_id = callback.data.split(":")[1]

    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        watchlist = json.load(f)

    user_watchlist = watchlist.get(str(callback.message.chat.id), [])
    for item in user_watchlist:
        if hashlib.md5(item["url"].encode()).hexdigest()[:10] == item_id:
            text = (
                f"🛍 **{item['title']}**\n"
                f"💰 Цена: {item['price1']} сум\n"
                f"[🔗 Перейти к товару]({item['url']})"
            )
            await callback.message.answer(text, parse_mode="Markdown", reply_markup=watchlist_item_keyboard(item))
            return


# Удаление товара
@market_router.callback_query(lambda c: c.data.startswith("del_item:"))
async def delete_item(callback: types.CallbackQuery):
    await callback.answer()
    item_id = callback.data.split(":")[1]
    chat_id = str(callback.message.chat.id)

    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        watchlist = json.load(f)

    user_watchlist = watchlist.get(chat_id, [])
    new_watchlist = [
        i for i in user_watchlist
        if hashlib.md5(i["url"].encode()).hexdigest()[:10] != item_id
    ]
    watchlist[chat_id] = new_watchlist

    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)

    await callback.message.answer(mt.TEXTS["delete_success"])

@market_router.callback_query(lambda c: c.data.startswith("add_to_watchlist_"))
async def add_to_watchlist(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = str(callback.message.chat.id)
    index = int(callback.data.split("_")[-1])

    products = products_cache.get(callback.message.chat.id)
    if not products or index >= len(products):
        await callback.message.answer(mt.TEXTS["product_not_found"])
        return

    product = products[index]

    try:
        with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
            watchlist = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        watchlist = {}

    if chat_id not in watchlist:
        watchlist[chat_id] = []

    if any(item["url"] == product["url"] for item in watchlist[chat_id]):
        await callback.message.answer(mt.TEXTS["already_in_watchlist"])
        return

    watchlist[chat_id].append({
        "title": product["title"],
        "price1": product["price"],
        "url": product["url"]
    })

    with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)

    await callback.message.answer(mt.TEXTS["add_success"])

@market_router.callback_query(lambda c: c.data.startswith("yandex_product_"))
async def yandex_product_detail_callback(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    products = products_cache.get(chat_id)
    if not products:
        await callback.message.answer(mt.TEXTS["products_load_error"])
        return

    index = int(callback.data.split("_")[-1])
    if index >= len(products):
        await callback.message.answer(mt.TEXTS["no_such_product"])
        return

    product = products[index]
    text = (
        f"✨🛍 **{product['title']}** ✨\n\n"
        f"💰 Цена: **{product['price']} сум**\n"
        f"📅 Оценка : *{product['rating']}*\n"
        f"🔗 [Открыть в Yandex]({product['url']})"
    )

    await callback.message.answer(text, parse_mode="Markdown", reply_markup=product_details_keyboard(product, index))


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
    loading_msg = await message.answer(mt.TEXTS["loading_categories"])

    try:
        categories = get_yandex_categories("https://market.yandex.uz/")
        categories_cache[chat_id] = categories
        await loading_msg.delete()
    except TimeoutException:
        await loading_msg.delete()
        await message.answer(mt.TEXTS["no_categories_y"])
        return

    text = (
        mt.TEXTS["yandex_welcome"]
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
            mt.TEXTS["no_categories_y"]
        )
        return

    await callback.message.edit_text(
        mt.TEXTS["choose_category"],
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
        await callback.message.answer(mt.TEXTS["not_found"])
        return

    loading_msg = await callback.message.answer(
        f"{mt.TEXTS['loading_products']} {category['title']}...",
        parse_mode="Markdown"
    )
    products = get_yandex_products(category["url"])
    await loading_msg.delete()

    if not products:
        await callback.message.answer(mt.TEXTS["no_products"])
        return

    products_cache[chat_id] = products

    await callback.message.edit_text(
        mt.TEXTS["products"], f"**{category['title'].replace('.', '\\.')}**\\.",
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
        await callback.message.answer(mt.TEXTS["products_load_error"])
        return

    text = mt.TEXTS["products_list"] + "\n\n"

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
