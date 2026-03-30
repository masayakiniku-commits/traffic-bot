import requests
from bs4 import BeautifulSoup
import time
import os

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 取締ワード
keywords = ["ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"]

# 対象エリア（軽量版）
areas = [
    # 名古屋16区
    "千種区","東区","北区","西区","中村区","中区","昭和区","瑞穂区",
    "熱田区","中川区","港区","南区","守山区","緑区","名東区","天白区",
    # その他
    "日進市","東郷町","みよし市"
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

                # 現在のYahoo構造に合わせてarticleタグ取得
                for item in soup.select("article"):
                    text = item.get_text(strip=True)
                    if text and text not in results:
                        results.append(text)
                time.sleep(0.1)  # 軽量化
            except Exception as e:
                print(f"Yahoo取得失敗: {query}, {e}")
                continue
    return results

# Discord通知
def send_discord(messages):
    import json
    for msg in messages:
        payload = {"content": f"🚨交通情報\n{msg}"}
        try:
            requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload),
                          headers={"Content-Type": "application/json"})
        except Exception as e:
            print(f"Discord送信失敗: {e}")

# メイン
if __name__ == "__main__":
    all_data = fetch_yahoo()
    print("取得件数:", len(all_data))
    for t in all_data[:20]:  # 上位20件表示
        print(t)

    if all_data:
        send_discord(all_data)
