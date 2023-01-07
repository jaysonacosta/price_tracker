import os
from time import sleep
from dotenv import load_dotenv
import pymongo
import requests
import datetime
from bs4 import BeautifulSoup

REQ_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip',
    'DNT': '1',
    'Connection': 'close'
}

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

client = pymongo.MongoClient(DATABASE_URL)

db = client.price_tracker

ENTRIES_COLLECTION = db.get_collection("entries")
PRICES_COLLECTION = db.get_collection("prices")

print("Successfully connected to database.")


while True:
    allEntries = ENTRIES_COLLECTION.find()
    for entry in allEntries:
        URL = entry['url']
        try:
            content = requests.get(URL, headers=REQ_HEADERS)
            soup = BeautifulSoup(content.text, "html.parser")

            title = soup.find(id="productTitle").text.strip()

            price = soup.find("span", {"id": "priceblock_ourprice"})
            image = soup.find(id="landingImage")["src"]

            if price == None:
                price = soup.find("span", {"class": "a-offscreen"})

            price = price.text.strip()

            price_entry = {"entryId": entry["_id"], "title": title, "image": image,
                           "price": price, "date": datetime.datetime.utcnow()}

            PRICES_COLLECTION.insert_one(price_entry)

            print("Successfully inserted price entry: ", title, "\n")

        except:
            print("Error fetching URL: ", URL)

    print("Refetching data in 24 hours.")
    sleep(86400)
