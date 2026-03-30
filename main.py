import requests
import os
from bs4 import BeautifulSoup

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

KEYWORDS = [
    "ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ",
    "パトカー", "取り締まり", "警察いた"
]

CITIES = [
    "名古屋","豊田","岡崎","一宮","豊橋","春日井","刈谷","安城",
    "西尾","小牧","稲沢","瀬戸","半田","東海"
]

def send_discord(msg):
    requests.post(WEBHOOK_URL, json={"content": msg})

# ■ Yahooリアルタイム検索
def fetch_yahoo():
    url = "https://search.yahoo.co.jp/realtime/search?p=オービス+白バイ+ネズミ捕り+愛知"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for item in soup.select("div.sw-CardBase"):
        text = item.get_text()
        results.append(text)

    return results

# ■ ニュース検索
def fetch_news():
    url = "https://news.yahoo.co.jp/search?p=交通取り締まり"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []

    for item in soup.select("a.newsFeed_item_link"):
        text = item.get_text()
        results.append(text)

    return results

def check_and_notify(texts):
    for text in texts:

        if not any(k in text for k in KEYWORDS):
            continue

        area_hit = any(city in text for city in CITIES)

        if area_hit:
            msg = f"🚨【愛知】交通取締\n{text}"
        else:
            msg = f"🚨交通情報\n{text}"

        print(msg)
        send_discord(msg)

def main():
    yahoo_data = fetch_yahoo()
    news_data = fetch_news()

    all_data = yahoo_data + news_data

    print("取得件数:", len(all_data))

    for t in all_data:
        print(t[:50])

    check_and_notify(all_data)

if __name__ == "__main__":
    main()
