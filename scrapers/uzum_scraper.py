from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from config import CHROME_PATH

OUTPUT_CATEGORY_FILE = "categories.json"
OUTPUT_PRODUCT_FILE = "products.json"

def get_uzum_categories(link):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(CHROME_PATH), options=options)

    all_categories = []
    try:
        driver.get(link)

        catalog_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-id='button__catalog']"))
        )
        catalog_btn.click()
        time.sleep(2)

        # Обычные категории
        categories = driver.find_elements(By.CSS_SELECTOR, "a[href^='/ru/category/']")
        for category in categories:
            title = category.text.strip()
            href = category.get_attribute("href")
            if title:
                all_categories.append({"title": title, "url": href, "type": "category"})

        # Добавляем промо “Товары недели”
        promo_link = "https://uzum.uz/ru/category/tovary-nedeli--895"
        all_categories.insert(0, {
            "title": "Товары недели",
            "url": promo_link,
            "type": "promo"
        })

    finally:
        driver.quit()

    # Сохраняем
    with open(OUTPUT_CATEGORY_FILE, "w", encoding="utf-8") as f:
        json.dump(all_categories, f, ensure_ascii=False, indent=4)

    return all_categories


def get_uzum_products(category_link):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(CHROME_PATH), options=options)

    all_products = []

    try:
        driver.get(category_link)
        time.sleep(5)

        products_cards = driver.find_elements(By.CSS_SELECTOR, "a.product-card")
        for card in products_cards:
            details = card.find_element(By.CSS_SELECTOR, "div.product-card__details")
            title = details.find_element(By.CSS_SELECTOR, "div.product-card__title").text
            price = details.find_element(By.CSS_SELECTOR, "span.card-price__regular").text
            price_per_month = details.find_element(By.CSS_SELECTOR, "span.card-price__installment").text
            url = card.get_attribute("href")
            all_products.append({
                "title": title,
                "price": price,
                "price_per_month": price_per_month,
                "url": url
            })

    finally:
        driver.quit()

    with open(OUTPUT_PRODUCT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)

    return all_products
