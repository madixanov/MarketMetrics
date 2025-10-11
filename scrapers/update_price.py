import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from pathlib import Path

WATCHLIST_FILE = "watchlist.json"

service = Service("chromedriver.exe")
options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
driver = webdriver.Chrome(service=service, options=options)

def get_price_from_page(url: str) -> int | None:
    """Парсит страницу товара и возвращает цену."""
    try:
        driver.get(url)
        price_el = driver.find_element(By.CSS_SELECTOR, "span.BodyLRegular.without-card")
        price_text = price_el.text.replace("Без карты Uzum", "").replace("сум", "")
        return price_text
    except Exception as e:
        print(f"Ошибка при парсинге {url}: {e}")
        return None

def update_prices():
    with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
        watchlist = json.load(f)

    updated = False
    today = datetime.now().strftime("%Y-%m-%d")

    for user_id, items in watchlist.items():
        for item in items:
            price = get_price_from_page(item["url"])
            if not price:
                continue
            
            if item["history"] and item["history"][-1]["date"] == today:
                continue

            item["history"].append({"date": today, "price": price})
            updated = True
            print(f"[{today}] Обновлено: {item['title']} — {price} сум")

    if updated:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=2)

    driver.quit()
    print("✅ Обновление завершено.")