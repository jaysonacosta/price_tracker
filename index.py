import requests
from bs4 import BeautifulSoup
import plotly.express as px
import pandas as pd
import datetime

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

price = soup.find("span", {"id": "priceblock_ourprice"})

data_frame = pd.DataFrame(
    dict(x=[today, "Tomorrow"], y=[price.text, "$400"]))
fig = px.line(data_frame, x="x", y="y")
fig.write_html('first_figure.html', auto_open=True)
