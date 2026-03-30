def fetch_yahoo():
    # ■ 取締ワード
    keywords = [
        "ネズミ捕り", "移動オービス", "オービス", "覆面", "白バイ"
    ]

    # ■ 愛知県 市町村＋名古屋16区
    areas = [
        # 名古屋市16区
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

    results = []

    # ■ 全組み合わせ検索
    for area in areas:
        for keyword in keywords:

            query = f"{area} {keyword}"
            url = f"https://search.yahoo.co.jp/realtime/search?p={query}"

            try:
                res = requests.get(url, timeout=5)
                soup = BeautifulSoup(res.text, "html.parser")

                for item in soup.select("article"):
                    text = item.get_text(strip=True)

                    if text and text not in results:
                        results.append(text)

            except:
                continue

    return results
