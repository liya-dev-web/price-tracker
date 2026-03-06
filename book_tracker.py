# ============================================================
#  BOOK PRICE TRACKER
#  Site: books.toscrape.com (made for scraping practice)
#  Skills: Python, Web Scraping, CSV, Price Alerts
# ============================================================
#
#  SETUP: pip install requests beautifulsoup4
#  RUN:   python book_tracker.py
# ============================================================

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time
import os
import random

# ── YOUR BOOKS TO TRACK ────────────────────────────────────
# These are real books on the practice site
# Target price is in GBP (£) — the site uses British pounds

BOOKS = [
    {
        "name": "A Light in the Attic",
        "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "target_price": 50.00,
    },
    {
        "name": "Tipping the Velvet",
        "url": "https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html",
        "target_price": 50.00,
    },
    {
        "name": "Soumission",
        "url": "https://books.toscrape.com/catalogue/soumission_998/index.html",
        "target_price": 50.00,
    },
]

CHECK_INTERVAL = 30    # check every 30 seconds (fast for learning)
CSV_FILE = "book_price_history.csv"

# ── GET PRICE ──────────────────────────────────────────────

def get_price(url):
    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print(f"  ⚠️  Status code: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.content, "html.parser")

        # Get book title
        title = soup.select_one("h1")
        title_text = title.get_text().strip() if title else "Unknown"

        # Get price — always inside <p class="price_color">
        price_element = soup.select_one("p.price_color")
        if price_element:
            raw = price_element.get_text().strip()
            # Remove £ sign and convert to float
            cleaned = raw.replace("£", "").replace("Â", "").strip()
            try:
                price = float(cleaned)
                return price, title_text
            except ValueError:
                print(f"  ⚠️  Could not convert price: {raw}")
                return None, title_text

        return None, title_text

    except requests.exceptions.RequestException as e:
        print(f"  ❌  Network error: {e}")
        return None, None


# ── SAVE TO CSV ────────────────────────────────────────────

def save_to_csv(book_name, price):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "book", "price_gbp"])
        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            book_name,
            price,
        ])


# ── CHECK ONE BOOK ─────────────────────────────────────────

def check_book(book):
    name         = book["name"]
    url          = book["url"]
    target_price = book["target_price"]

    print(f"\n  Checking: {name}")

    price, page_title = get_price(url)

    if price is None:
        print(f"  ❌  Could not get price")
        return

    print(f"  ✅  Price found:  £{price:.2f}")
    print(f"  🎯  Your target: £{target_price:.2f}")

    save_to_csv(name, price)
    print(f"  💾  Saved to {CSV_FILE}")

    if price <= target_price:
        print(f"  🎉  PRICE ALERT! £{price:.2f} is at or below your target!")
    else:
        diff = price - target_price
        print(f"  ⏳  £{diff:.2f} above your target")


# ── MAIN LOOP ──────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  📚  Book Price Tracker")
    print(f"  Tracking {len(BOOKS)} book(s)")
    print(f"  Checking every {CHECK_INTERVAL} seconds")
    print(f"  Saving to: {CSV_FILE}")
    print("=" * 55)

    check_count = 0
    while True:
        check_count += 1
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n{'─' * 55}")
        print(f"  Check #{check_count}  |  {now}")
        print(f"{'─' * 55}")

        for book in BOOKS:
            check_book(book)
            time.sleep(1)

        print(f"\n  ✅  Done. Next check in {CHECK_INTERVAL} seconds.")
        print(f"  (Press Ctrl+C to stop)\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Tracker stopped.")
        print(f"  Open {CSV_FILE} in Excel to see your price history.\n")
