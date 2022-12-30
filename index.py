import os
from dotenv import load_dotenv
import pymongo
import requests
import datetime
from bs4 import BeautifulSoup

load_dotenv()

MONGODB_PASSWORD = os.getenv("MONGO_PASSWORD")

client = pymongo.MongoClient(
    f'mongodb+srv://admin:{MONGODB_PASSWORD}@cluster0.funxtlf.mongodb.net/?retryWrites=true&w=majority')

db = client.price_tracker

ENTRIES_COLLECTION = db.get_collection("entries")
PRICES_COLLECTION = db.get_collection("prices")

URL_LIST = ["https://www.amazon.com/Nintendo-Switch-OLED-Model-White-Joy/dp/B098RKWHHZ/ref=sr_1_4?keywords=nintendo%2Bswitch&qid=1672248113&sprefix=ninten%2Caps%2C76&sr=8-4&th=1"]

REQ_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'DNT': '1',
    'Connection': 'close'
}

date = datetime.datetime.now()
today = date.strftime("%x")

content = requests.get(URL_LIST[0], headers=REQ_HEADERS)

soup = BeautifulSoup(content.text, "html.parser")

title = soup.find("span", {"id": "productTitle"}).text.strip()
price = soup.find("span", {"id": "priceblock_ourprice"}).text.strip()

entryExists = ENTRIES_COLLECTION.find_one({"title": title})

if entryExists == None:
    ENTRIES_COLLECTION.insert_one(
        {"title": title, "date": datetime.datetime.utcnow()})

existingEntry = ENTRIES_COLLECTION.find_one({"title": title})

price_entry = {"entryId": existingEntry["_id"], "title": title,
               "price": price, "date": datetime.datetime.utcnow()}


PRICES_COLLECTION.insert_one(price_entry)
