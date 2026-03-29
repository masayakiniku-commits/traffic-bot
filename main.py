
import requests
import os
import json
import re
from datetime import datetime, timedelta

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

SEEN_FILE = "seen_ids.json"

MAIN_KEYWORDS = [
    "ネズミ捕り",
    "移動オービス",
    "オービス",
    "覆面",
    "覆面パトカー",
    "白バイ"
]

AREA_KEYWORDS = [
    "名古屋市",
    "千種区","東区","北区","西区","中村区","中区","昭和区",
    "瑞穂区","熱田区","中川区","港区","南区","守山区",
    "緑区","名東区","天白区",

    "豊橋市","岡崎市","一宮市","瀬戸市","半田市","春日井市","豊川市",
    "津島市","碧南市","刈谷市","豊田市","安城市","西尾市","蒲郡市",
    "犬山市","常滑市","江南市","小牧市","稲沢市","新城市","東海市",
    "大府市","知多市","知立市","尾張旭市","高浜市","岩倉市","豊明市",
    "日進市","田原市","愛西市","清須市","北名古屋市","弥富市",
    "みよし市","あま市","長久手市",

    "東郷町","豊山町","大口町","扶桑町","大治町","蟹江町",
    "阿久比町","東浦町","南知多町","美浜町","武豊町","幸田町",
    "設楽町","東栄町",

    "飛島村","豊根村"
]

SUB_AREA_KEYWORDS = ["名駅","栄","金山","今池","大曽根"]

NG_KEYWORDS = [
    "事故","渋滞","工事","ニュース","動画",
    "YouTube","まとめ","過去","昨日","ドラレコ"
]

# ----------------------
# 重複防止（永続）
# ----------------------
def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))

def save_seen(seen_ids):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_ids)[-200:], f)  # 最大200件保存

SEEN_IDS = load_seen()

def is_new(tweet_id):
    if tweet_id in SEEN_IDS:
        return False
    SEEN_IDS.add(tweet_id)
    return True

# ----------------------
# 検索
# ----------------------
def create_query():
    main = " OR ".join(MAIN_KEYWORDS)
    return f"({main}) -is:retweet -is:reply -has:links lang:ja"

def search_tweets():
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    params = {
        "query": create_query(),
        "max_results": 10,
        "tweet.fields": "created_at,text"
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        return res.json()
    except Exception as e:
        print("取得エラー:", e)
        return {}

# ----------------------
# フィルタ
# ----------------------
def is_valid(text, created_at):
    if not (
        any(area in text for area in AREA_KEYWORDS) or
        any(area in text for area in SUB_AREA_KEYWORDS)
    ):
        return False

    if any(ng in text for ng in NG_KEYWORDS):
        return False

    if not any(word in text for word in ["今","現在","やってる","実施中"]):
        return False

    tweet_time = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    if datetime.utcnow() - tweet_time > timedelta(hours=1):
        return False

    return True

# ----------------------
# 地点抽出
# ----------------------
def extract_location(text):
    patterns = [
        r'([^\s]+交差点)',
        r'([^\s]+駅)',
        r'([^\s]+IC)',
        r'([^\s]+付近)',
        r'([^\s]+周辺)',
        r'([^\s]+道路)',
        r'([^\s]+線)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None

def create_map_link(location):
    if not location:
        return ""
    return f"https://www.google.com/maps/search/{location}"

# ----------------------
# 通知
# ----------------------
def build_message(text):
    location = extract_location(text)
    map_link = create_map_link(location)

    message = f"🚨交通取り締まり情報\n{text}"

    if location:
        message += f"\n📍{location}"
    if map_link:
        message += f"\n🗺 {map_link}"

    return message

def send_to_discord(text):
    try:
        requests.post(WEBHOOK_URL, json={"content": text}, timeout=10)
    except Exception as e:
        print("送信エラー:", e)

# ----------------------
# メイン
# ----------------------
def main():
    data = search_tweets()

    if "data" not in data:
        print("投稿なし or 取得失敗")
        return

    count = 0

    for tweet in data["data"]:
        if not is_new(tweet["id"]):
            continue

        text = tweet["text"]
        created_at = tweet["created_at"]

        if is_valid(text, created_at):
            message = build_message(text)
            send_to_discord(message)
            count += 1

    save_seen(SEEN_IDS)

    print(f"通知数: {count}")

if __name__ == "__main__":
    main()
