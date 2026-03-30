import requests
import os
import time

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 検知ワード
KEYWORDS = [
    "ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"
]

# 愛知県市町村（主要だけ抜粋＋両対応）
CITIES = [
    "名古屋", "名古屋市",
    "豊田", "豊田市",
    "岡崎", "岡崎市",
    "一宮", "一宮市",
    "豊橋", "豊橋市",
    "春日井", "春日井市",
    "刈谷", "刈谷市",
    "安城", "安城市",
    "西尾", "西尾市",
    "小牧", "小牧市",
    "稲沢", "稲沢市",
    "瀬戸", "瀬戸市",
    "半田", "半田市",
    "東海", "東海市"
]

def create_headers():
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}

def search_tweets():
    query = " OR ".join(KEYWORDS)

    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": query + " -is:retweet lang:ja",
        "max_results": 10
    }

    response = requests.get(url, headers=create_headers(), params=params)

    if response.status_code != 200:
        print("取得失敗:", response.text)
        return []

    return response.json().get("data", [])

def send_discord(message):
    requests.post(WEBHOOK_URL, json={"content": message})

def main():
    tweets = search_tweets()

    for tweet in tweets:
        text = tweet["text"]

        # キーワード判定
        if not any(k in text for k in KEYWORDS):
            continue

        # 地名判定（ゆるめ）
        area_hit = any(city in text for city in CITIES)

        # 条件：キーワードあればOK（地名は参考）
        msg = f"🚨交通取締情報\n{text}"

        if area_hit:
            msg = f"🚨【愛知】交通取締\n{text}"

        print(msg)
        send_discord(msg)

if __name__ == "__main__":
    main()
