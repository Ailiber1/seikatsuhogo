"""厚労省が案内している「令和7年度 自立相談支援機関窓口情報」(minna-tunagaru.jp)から
全都道府県の相談窓口一覧を取得し、JSONにする。
出典: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000059425.html が案内するページ
"""
import html
import json
import re
import time
import urllib.request

S = "/private/tmp/claude-501/-private-tmp/4b42560e-3aa8-4bc5-8b88-2482dc59f9cb/scratchpad"
BASE = "https://minna-tunagaru.jp"
UA = {"User-Agent": "Mozilla/5.0"}

# 都道府県ページのスラッグ一覧を取得
idx = urllib.request.urlopen(urllib.request.Request(BASE + "/ichiran/", headers=UA), timeout=30).read().decode("utf-8", "ignore")
slugs = sorted(set(re.findall(r'href="/ichiran/([a-z]+)#', idx)))
print("都道府県ページ:", len(slugs), "件")

# ページ内の見出しから都道府県名を拾うためのスラッグ→名前対応
PREF = {
 "hokkaido":"北海道","aomori":"青森県","iwate":"岩手県","miyagi":"宮城県","akita":"秋田県",
 "yamagata":"山形県","fukushima":"福島県","ibaraki":"茨城県","tochigi":"栃木県","gunma":"群馬県",
 "saitama":"埼玉県","chiba":"千葉県","tokyo":"東京都","kanagawa":"神奈川県","nigata":"新潟県",
 "toyama":"富山県","ishikawa":"石川県","fukui":"福井県","yamanashi":"山梨県","nagano":"長野県",
 "gifu":"岐阜県","shizuoka":"静岡県","aichi":"愛知県","mie":"三重県","shiga":"滋賀県",
 "kyoto":"京都府","osaka":"大阪府","hyougo":"兵庫県","nara":"奈良県","wakayama":"和歌山県",
 "tottori":"鳥取県","shimane":"島根県","okayama":"岡山県","hiroshima":"広島県","yamaguchi":"山口県",
 "tokushima":"徳島県","kagawa":"香川県","ehime":"愛媛県","kouchi":"高知県","fukuoka":"福岡県",
 "saga":"佐賀県","nagasaki":"長崎県","kumamoto":"熊本県","oita":"大分県","miyazaki":"宮崎県",
 "kagoshima":"鹿児島県","okinawa":"沖縄県",
}


def cells_of(row):
    out = []
    for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S):
        t = re.sub(r"<br\s*/?>", "\n", c)
        t = html.unescape(re.sub(r"<[^>]+>", "", t)).strip()
        out.append(t)
    return out


DATA = {}
missing = []
for slug in slugs:
    pref = PREF.get(slug)
    if not pref:
        missing.append(slug)
        continue
    url = f"{BASE}/ichiran/{slug}/"
    try:
        s = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read().decode("utf-8", "ignore")
    except Exception as e:
        print("  取得失敗:", slug, e)
        continue
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S)
    items = []
    for r in rows:
        c = cells_of(r)
        if len(c) < 4 or c[0] in ("お住まいの自治体名", ""):
            continue
        mail = re.findall(r'href="mailto:([^"]+)"', r)
        items.append({
            "city": c[0],
            "name": c[1],
            "addr": c[2],
            "tel": c[3],
            "mail": mail[0] if mail else "",
        })
    DATA[pref] = items
    print(f"  {pref}: {len(items)}件")
    time.sleep(0.4)   # 相手サイトに負荷をかけないよう間隔をあける

if missing:
    print("スラッグ未対応:", missing)
total = sum(len(v) for v in DATA.values())
print("\n都道府県:", len(DATA), "／ 窓口数:", total)
json.dump({"source": "令和7年度 自立相談支援機関窓口情報（厚生労働省が案内する一覧）",
           "url": "https://minna-tunagaru.jp/ichiran/",
           "mhlw": "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000059425.html",
           "slugs": PREF, "data": DATA},
          open(f"{S}/madoguchi.json", "w", encoding="utf-8"), ensure_ascii=False)
print("保存:", f"{S}/madoguchi.json")
