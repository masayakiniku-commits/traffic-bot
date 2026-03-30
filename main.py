import requests
import os

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 検知ワード（増やしてヒット率UP）
KEYWORDS = [
    "ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ",
    "パトカー", "取り締まり", "警察いた"
]

# 愛知（市あり・なし両対応）
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
    # クエリ強化（愛知系も含める）
    query = "(" + " OR ".join(KEYWORDS) + ") (愛知 OR 名古屋 OR 岡崎 OR 一宮) lang:ja -is:retweet"

    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": query,
        "max_results": 10
    }

    res = requests.get(url, headers=create_headers(), params=params)

    if res.status_code != 200:
        print("取得失敗:", res.text)
        return []

    return res.json().get("data", [])

def send_discord(message):
    requests.post(WEBHOOK_URL, json={"content": message})

def main():
    tweets = search_tweets()

    # ★ デバッグ（超重要）
    print("取得ツイート数:", len(tweets))
    for t in tweets:
        print(t["text"])
        print("------")

    for tweet in tweets:
        text = tweet["text"]

        # キーワードチェック
        if not any(k in text for k in KEYWORDS):
            continue

        # 地名チェック（あれば愛知扱い）
        area_hit = any(city in text for city in CITIES)

        if area_hit:
            msg = f"🚨【愛知】交通取締\n{text}"
        else:
            msg = f"🚨交通情報\n{text}"

        print("送信:", msg)
        send_discord(msg)

if __name__ == "__main__":
    main()
