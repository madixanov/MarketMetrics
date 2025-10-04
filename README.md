# 🛒 MarketMetrics

**MarketMetrics** is a Telegram bot that collects and analyzes data from online marketplaces.  
It allows users to track product categories, prices, and performance metrics directly in Telegram.

---

## 📘 Description

MarketMetrics automates data collection using **Selenium** and provides real-time access to product analytics through a **Telegram bot** built with **Aiogram**.  
The project is modular, easy to extend, and organized for scalability.

---

## 🧱 Project Structure


```bash
MarketMetrics/
├── bot.py # Entry point — runs the Telegram bot
├── config.py # Loads environment variables
├── handlers/ # Message and command handlers
│ ├── start.py
│ ├── help.py
│ └── market.py
├── keyboards/ # Inline buttons
│ └── inline.py
├── scrapers/ # Gets data from marketplaces
│ ├── categories.json
│ ├── products.json
│ ├── uzum_scraper.py
│ └── yandex_scraper.py
├── .env # Environment configuration file
├── requirements.txt # Dependencies list
└── README.md # Project documentation
```

---

## ⚙️ Features

- 🤖 Telegram bot interface powered by **Aiogram**
- 🌐 Marketplace parsing with **Selenium**
- 💾 Local JSON and database data storage
- 📊 Product and category analytics
- 🧱 Modular, scalable architecture

---

## 🧰 Technologies Used

- **Python 3.11+**
- **Aiogram** – asynchronous Telegram framework  
- **Selenium** – for browser automation and scraping  
- **Asyncio** – concurrency for polling and tasks  
- **python-dotenv** – environment variable management  
- **JSON** – data storage and configuration  


