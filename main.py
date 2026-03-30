import requests
from bs4 import BeautifulSoup
import os

# ==============================
# ■ 通知先（Discord webhook）
# ==============================
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# ==============================
# ■ 検知キーワード（強化版）
# ==============================
KEYWORDS = [
    "オービス","移動オービス",
    "覆面","覆面パト","覆面パトカー",
    "白バイ","取締","ネズミ捕り","検問"
]

# ==============================
# ■ エリア（愛知フル＋名古屋16区）
# ==============================
AREAS = [
# 名古屋
"名古屋","名古屋市",
"千種","千種区","東","東区","北","北区","西","西区",
"中村","中村区","中","中区","昭和","昭和区","瑞穂","瑞穂区",
"熱田","熱田区","中川","中川区","港","港区","南","南区",
"守山","守山区","緑","緑区","名東","名東区","天白","天白区",

# 市
"豊橋","豊橋市","岡崎","岡崎市","一宮","一宮市","瀬戸","瀬戸市",
"半田","半田市","春日井","春日井市","豊川","豊川市","津島","津島市",
"碧南","碧南市","刈谷","刈谷市","豊田","豊田市","安城","安城市",
"西尾","西尾市","蒲郡","蒲郡市","犬山","犬山市","常滑","常滑市",
"江南","江南市","小牧","小牧市","稲沢","稲沢市","新城","新城市",
"東海","東海市","大府","大府市","知多","知多市","知立","知立市",
"尾張旭","尾張旭市","高浜","高浜市","岩倉","岩倉市","豊明","豊明市",
"日進","日進市","田原","田原市","愛西","愛西市","清須","清須市",
"北名古屋","北名古屋市","弥富","弥富市","みよし","みよし市",
"あま","あま市","長久手","長久手市",

# 町村
"東郷","東郷町","豊山","豊山町","大口","大口町","扶桑","扶桑町",
"大治","大治町","蟹江","蟹江町","阿久比","阿久比町","東浦","東浦町",
"南知多","南知多町","美浜","美浜町","武豊","武豊町","幸田","幸田町",
"設楽","設楽町","東栄","東栄町",
"飛島","飛島村","豊根","豊根村"
]

# ==============================
# ■ Yahooリアルタイム検索
# ==============================
def get_yahoo():
    url = "https://search.yahoo.co.jp/realtime/search?p=オービス+愛知"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []
    for item in soup.select("article"):
        text = item.get_text()
        results.append(text)

    return results

# ==============================
# ■ フィルタ
# ==============================
def filter_posts(posts):
    hit_posts = []

    for text in posts:
        if any(k in text for k in KEYWORDS) and any(a in text for a in AREAS):
            hit_posts.append(text)

    return hit_posts

# ==============================
# ■ Discord送信
# ==============================
def send_discord(msg):
    if not WEBHOOK_URL:
        print("Webhook未設定")
        return

    data = {"content": msg}
    requests.post(WEBHOOK_URL, json=data)

# ==============================
# ■ メイン処理
# ==============================
def main():
    posts = []

    # Yahoo取得
    try:
        posts += get_yahoo()
    except Exception as e:
        print("Yahoo取得失敗:", e)

    print("取得件数:", len(posts))

    hits = filter_posts(posts)

    print("検知件数:", len(hits))

    for h in hits[:5]:
        send_discord("🚨検知\n" + h[:200])

if __name__ == "__main__":
    main()
