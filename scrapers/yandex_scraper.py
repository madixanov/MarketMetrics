from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from dotenv import load_dotenv

load_dotenv()
CHROME_PATH = os.getenv("CHROME_PATH")

def get_yandex_products(category_link):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(CHROME_PATH), options=options)
    all_products = []

    try:
        driver.get(category_link)
        wait = WebDriverWait(driver, 10)

        products_cards = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-id]'))
        )

        for card in products_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, '[data-zone-name="title"]').text
            except:
                title = "Нет названия"

            try:
                price = card.find_element(By.CSS_SELECTOR, '[data-zone-name="price"]').text
            except:
                price = "Нет цены"

            try:
                rating = card.find_element(By.CSS_SELECTOR, '[data-zone-name="rating"]').text
            except:
                rating = "Нет рейтинга"

            try:
                link = card.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
            except:
                link = "Нет ссылки"

            all_products.append({
                "title": title,
                "price": price,
                "rating": rating,
                "link": link
            })

        return all_products

    finally:
        driver.quit()


if __name__ == "__main__":
    category_link = "https://market.yandex.uz/catalog--odezhda-obuv-i-aksessuary/54432/list"
    products = get_yandex_products(category_link)

    print(f"Найдено товаров: {len(products)}\n")
    for i, p in enumerate(products, start=1):
        print(f"{i}. {p['title']}")
        print(f"   Цена: {p['price']}")
        print(f"   Рейтинг: {p['rating']}")
        print(f"   Ссылка: {p['link']}\n")
