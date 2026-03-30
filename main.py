import requests
from bs4 import BeautifulSoup
import time
import os
import json

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 取締ワード
keywords = ["ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"]

# 交通文脈ワード（AND条件）
traffic_words = ["道路", "交差点", "区", "警察", "取締り", "速度", "高速", "車線"]

# ノイズ除外ワード
noise_words = ["ゲーム", "漫画", "動画", "アニメ", "見つかりません", "投稿はありません"]

# 対象エリア
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

                    # ノイズ除外
                    if any(n in text for n in noise_words):
                        continue

                    # AND条件チェック
                    if text and any(k in text for k in keywords) and any(t in text for t in traffic_words):
                        if text not in results:
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

    print("取得件数:", len(data))
    for t in data[:20]:  # 上位20件表示
        print(t)

    if data:
        send_discord(data)
