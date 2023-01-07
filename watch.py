import os
from dotenv import load_dotenv
import pymongo
import requests
import datetime
from bs4 import BeautifulSoup
from bson.objectid import ObjectId

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
URLS_COLLECTION = db.get_collection("urls")

print("Successfully connected to database. Now watching for changes...\n")

collectionWatch = URLS_COLLECTION.watch()
for update in collectionWatch:

    print(update)
    URL = update['fullDocument']['url']
    content = None

    try:
        content = requests.get(URL, headers=REQ_HEADERS)
        soup = BeautifulSoup(content.text, "html.parser")

        title = soup.find(id="productTitle").text.strip()

        price = soup.find("span", {"id": "priceblock_ourprice"})
        image = soup.find(id="landingImage")["src"]

        if price == None:
            price = soup.find("span", {"class": "a-offscreen"})

        price = price.text.strip()

        entryExists = ENTRIES_COLLECTION.find_one({"title": title})

        if entryExists == None:
            result = ENTRIES_COLLECTION.insert_one(
                {"title": title, "image": image, "date": datetime.datetime.utcnow(), "url": URL})

            insertedId = result.inserted_id

            price_entry = {"entryId": insertedId, "title": title, "image": image,
                           "price": price, "date": datetime.datetime.utcnow(), }

            PRICES_COLLECTION.insert_one(price_entry)

            print("Successfully inserted price entry: ", title, "\n")

            continue

        print("Entry already exists.\n")

    except:
        print("Error fetching URL: ", URL, "\n")
