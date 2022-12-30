import os
from dotenv import load_dotenv
import pymongo
import requests
import datetime
from bs4 import BeautifulSoup

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

client = pymongo.MongoClient(DATABASE_URL)

db = client.price_tracker

ENTRIES_COLLECTION = db.get_collection("entries")
PRICES_COLLECTION = db.get_collection("prices")

URL_LIST = ["https://www.amazon.com/Nintendo-Switch-OLED-Model-White-Joy/dp/B098RKWHHZ/ref=sr_1_4?keywords=nintendo%2Bswitch&qid=1672248113&sprefix=ninten%2Caps%2C76&sr=8-4&th=1",
            "https://www.amazon.com/Nintendo-Switch-Lite-Blue/dp/B092VT1JGD/ref=sr_1_1?crid=37HSE0FP7ZH3X&keywords=switch+lite&qid=1672418377&sr=8-1&ufe=app_do%3Aamzn1.fos.f5122f16-c3e8-4386-bf32-63e904010ad0",
            "https://www.amazon.com/Legend-Zelda-Breath-Wild-switch-Nintendo/dp/B01N1083WZ/ref=sr_1_2?crid=NSKPGQ72VKUM&keywords=nintendo+switch+lite+zelda&qid=1672418412&sr=8-2&ufe=app_do%3Aamzn1.fos.006c50ae-5d4c-4777-9bc0-4513d670b6bc",
            "https://www.amazon.com/PlayStation-5-Console/dp/B0BCNKKZ91/ref=sr_1_2?crid=2955K5TLIEWUF&keywords=playstation+5&qid=1672418940&sprefix=playst%2Caps%2C81&sr=8-2"]

REQ_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'close'
}

date = datetime.datetime.now()
today = date.strftime("%x")

for URL in URL_LIST:
    content = requests.get(URL, headers=REQ_HEADERS)

    soup = BeautifulSoup(content.text, "html.parser")

    title = soup.find("span", {"id": "productTitle"}).text.strip()
    price = soup.find("span", {"id": "priceblock_ourprice"})
    if price == None:
        price = soup.find("span", {"class": "a-offscreen"})

    price = price.text.strip()

    entryExists = ENTRIES_COLLECTION.find_one({"title": title})

    if entryExists == None:
        ENTRIES_COLLECTION.insert_one(
            {"title": title, "date": datetime.datetime.utcnow()})

    existingEntry = ENTRIES_COLLECTION.find_one({"title": title})

    price_entry = {"entryId": existingEntry["_id"], "title": title,
                   "price": price, "date": datetime.datetime.utcnow()}

    PRICES_COLLECTION.insert_one(price_entry)
