import requests
from bs4 import BeautifulSoup
import time
import os

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# 取締ワード
keywords = ["ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"]

# 愛知県 全市町村 + 名古屋16区
areas = [
    # 名古屋16区
    "千種区","東区","北区","西区","中村区","中区","昭和区","瑞穂区",
    "熱田区","中川区","港区","南区","守山区","緑区","名東区","天白区",
    # 市
    "豊橋市","岡崎市","一宮市","瀬戸市","半田市","春日井市","豊川市",
    "津島市","碧南市","刈谷市","豊田市","安城市","西尾市","蒲郡市",
    "犬山市","常滑市","江南市","小牧市","稲沢市","新城市","東海市",
    "大府市","知多市","知立市","尾張旭市","高浜市","岩倉市","豊明市",
    "日進市","田原市","愛西市","清須市","北名古屋市","弥富市",
    "みよし市","あま市","長久手市",
    # 町村
    "東郷町","豊山町","大口町","扶桑町","大治町","蟹江町",
    "阿久比町","東浦町","南知多町","美浜町","武豊町",
    "幸田町","設楽町","東栄町","飛島村","豊根村"
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
                time.sleep(0.3)  # 連続アクセス軽減
            except Exception as e:
                print(f"Yahoo取得失敗: {query}, {e}")
                continue
    return results

# 他の情報サイト（例：交通安全情報サイトRSS）
def fetch_other_sites():
    results = []
    rss_urls = [
        "https://www.kotsu-anzen.jp/rss/notice.xml",  # 仮のRSS例
    ]
    for url in rss_urls:
        try:
            res = requests.get(url, timeout=5)
            soup = BeautifulSoup(res.text, "xml")
            for item in soup.find_all("item"):
                text = item.title.get_text(strip=True)
                if any(k in text for k in keywords) and text not in results:
                    results.append(text)
        except Exception as e:
            print(f"他サイト取得失敗: {url}, {e}")
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
    all_data = []

    # Yahoo取得
    yahoo_data = fetch_yahoo()
    all_data.extend(yahoo_data)

    # 他サイト取得
    other_data = fetch_other_sites()
    all_data.extend(other_data)

    # 重複削除
    all_data = list(dict.fromkeys(all_data))

    print("取得件数:", len(all_data))
    for t in all_data[:20]:  # 上位20件だけ表示
        print(t)

    # Discord送信
    if all_data:
        send_discord(all_data)
