import requests
from bs4 import BeautifulSoup
import time
import os
import json

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 取締ワード
keywords = ["ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"]

# 交通文脈ワード（AND条件チェック用）
traffic_words = ["道路", "交差点", "区", "警察", "取締り", "速度", "高速", "車線"]

# 対象エリア（名古屋16区 + 日進市 + 東郷町 + みよし市 + 長久手市）
areas = [
    # 名古屋16区
    "千種区","東区","北区","西区","中村区","中区","昭和区","瑞穂区",
    "熱田区","中川区","港区","南区","守山区","緑区","名東区","天白区",
    # その他
    "日進市","東郷町","みよし市","長久手市"
]

# Yahooリアルタイム検索取得
def fetch_yahoo():
    results = []

    for area in areas:
        for keyword in keywords:
            query = f"{area} {keyword}"
            url = f"https://search.yahoo.co.jp/realtime/search?p={query}"

            try:
                res = requests.get(url, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")

                for item in soup.select("article"):
                    text = item.get_text(strip=True)
                    # AND条件でフィルタ
                    if text and text not in results and any(t in text for t in traffic_words):
                        results.append(text)
                time.sleep(0.1)  # 軽量化
            except Exception as e:
                print(f"Yahoo取得失敗: {query}, {e}")
                continue
    return results

# Discord通知
def send_discord(messages):
    for msg in messages:
        payload = {"content": f"🚨交通情報\n{msg}"}
        try:
            requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload),
                          headers={"Content-Type": "application/json"})
        except Exception as e:
            print(f"Discord送信失敗: {e}")

# メイン
if __name__ == "__main__":
    data = fetch_yahoo()

    # 重複削除
    data = list(dict.fromkeys(data))

    print("取得件数:", len(data))
    for t in data[:20]:  # 上位20件表示
        print(t)

    if data:
        send_discord(data)
