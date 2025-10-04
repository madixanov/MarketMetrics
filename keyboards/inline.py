from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pathlib import Path
import hashlib
import json


# ================================
# Absolute Path to categories.json
# ================================
CATEGORIES_PATH = Path(__file__).parent.parent / "scrapers" / "categories.json"


# ===============================
# Loading category data from JSON
# ===============================
def load_uzum_categories():
    """Safe load"""
    try:
        with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


# ============
# Start Button
# ============
def start_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🚀 Start", callback_data="start_bot")
    )
    return kb.as_markup()


# ===================
# Marketplace Buttons
# ===================
def marketplace_keyboard():
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text="🍇 Uzum Market", callback_data="market_uzum"),
        InlineKeyboardButton(text="🟨 Yandex Market", callback_data="market_yandex")
    )
    return kb.as_markup()


# ==========
# Pagination
# ==========
CATEGORIES_PAGE_SIZE = 6
PRODUCTS_PAGE_SIZE = 6


# =======================
# Uzum Categories Buttons
# =======================
def uzum_categories_keyboard(categories, page: int = 0):
    total = len(categories)
    start = page * CATEGORIES_PAGE_SIZE
    end = start + CATEGORIES_PAGE_SIZE
    current_page_items = categories[start:end]

    kb = InlineKeyboardBuilder()
    
    # Категории в колонку
    for c in current_page_items:
        text = c["title"]
        callback_data = f"uzum_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        kb.row(InlineKeyboardButton(text=text, callback_data=callback_data))

    # Навигация в колонку
    if page > 0:
        kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"uzum_page_{page-1}"))
    if end < total:
        kb.row(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"uzum_page_{page+1}"))

    # Кнопка "Назад"
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="start_bot"))

    return kb.as_markup()


# =======================
# Uzum Products Buttons
# =======================
def uzum_products_keyboard(products, page=0):
    kb = InlineKeyboardBuilder()
    start = page * PRODUCTS_PAGE_SIZE
    end = start + PRODUCTS_PAGE_SIZE
    current_products = products[start:end]

    for i, p in enumerate(current_products, start=start):
        kb.row(InlineKeyboardButton(
            text=p['title'],
            callback_data=f"product_{i}"  # индекс вместо хэша
        ))

    # Навигация
    if page > 0:
        kb.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"products_page_{page-1}"))
    if end < len(products):
        kb.row(InlineKeyboardButton(text="Вперёд ➡️", callback_data=f"products_page_{page+1}"))

    # Кнопка "Назад к категориям"
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories"))

    return kb.as_markup()


# ============================
# Uzum Product Details Buttons
# ============================
def uzum_product_details_keyboard(product):
    kb = InlineKeyboardBuilder()

    kb.row(InlineKeyboardButton(text="🔗 Перейти по ссылке", url=product['url']))
    kb.row(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_products"))

    return kb.as_markup()


# =======================
# Yandex Categories Buttons
# =======================
def yandex_categories_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="🔙 Назад", callback_data="start_bot"))

    return kb.as_markup()

