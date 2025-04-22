import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import hashlib

# Configuration
URLS = [
    "https://www.example.com/category/mini-gt",
    "https://www.example.com/category/mini-gt?page=2",
    "https://www.example.com/category/hot-wheels-mainlines",
    "https://www.example.com/category/hot-wheels-premium",
]

CHECK_INTERVAL = 60  # Seconds
STATE_FILE = "stock_state.csv"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL")
DISCORD_USER_ID = os.getenv("DISCORD_USER_ID", "user_id_here")

def send_to_discord(content):
    if not DISCORD_WEBHOOK:
        print("⚠️ No Discord webhook set. Skipping alert.")
        return
    try:
        data = {"content": content}
        response = requests.post(DISCORD_WEBHOOK, json=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

def generate_unique_id(product_name, product_price):
    unique_string = product_name + product_price
    return hashlib.md5(unique_string.encode('utf-8')).hexdigest()

def get_product_data(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        products = []
        for div in soup.find_all("div", class_="show-product-small-bx"):
            product_id = div.get("data-latest", "").strip()
            name_tag = div.find("h3")
            product_name = name_tag.text.strip() if name_tag else "Unknown Product"
            price_tag = div.find("span", class_="rs")
            product_price = price_tag.text.strip() if price_tag else "Price N/A"
            if not product_id:
                product_id = generate_unique_id(product_name, product_price)
            products.append({
                "url": url,
                "id": product_id,
                "name": product_name,
                "price": product_price
            })
        return products
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

def load_previous_state():
    state = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, mode="r", newline='', encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    url = row["url"]
                    prod_id = row["id"]
                    state.setdefault(url, set()).add(prod_id)
        except Exception as e:
            print(f"Error loading CSV state: {e}")
    return state

def save_current_state(all_products):
    try:
        with open(STATE_FILE, mode="w", newline='', encoding="utf-8") as csvfile:
            fieldnames = ["url", "id", "name", "price"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for product in all_products:
                writer.writerow(product)
    except Exception as e:
        print(f"Error writing to CSV: {e}")

def monitor():
    while True:
        previous_state = load_previous_state()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"🔍 Checking {len(URLS)} URLs at {timestamp}")
        send_to_discord(f"🔍 Checking {len(URLS)} URLs at {timestamp}")

        current_state = {}
        all_current_products = []

        for url in URLS:
            current_products = get_product_data(url)
            current_ids = {product["id"] for product in current_products}
            all_current_products.extend(current_products)

            previous_ids = previous_state.get(url, set())
            new_ids = current_ids - previous_ids
            new_items = [p for p in current_products if p["id"] in new_ids]

            if new_items:
                alert_msg = f"🚨 NEW ITEMS FOUND ON {url}\n"
                for item in new_items:
                    alert_msg += f"• {item['name']} - {item['price']}\n"
                alert_msg += f"\n<@{DISCORD_USER_ID}> 🔥 New stock available!"
                print(alert_msg)
                send_to_discord(alert_msg)

            current_state[url] = current_ids
            print(f"✓ Checked: {url} ({len(current_products)} items)")

        save_current_state(all_current_products)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("🚀 Starting Stock Monitor...")
    monitor()
