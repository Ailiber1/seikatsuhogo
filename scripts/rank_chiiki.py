"""data/chiiki.json と data/gomi_bag.json から、52都市の「生活保護で暮らしやすいか」の物差しと順位を計算し、
data/chiiki_rank.json に書き出す。資料（chiiki-setsumei.html）とツール（chiiki.html）はこの結果を使う。

使い方: python3 scripts/rank_chiiki.py

物差し（どれも試算。単位がちがうので、順位どうしを足して総合順位にする）
 1 物価で見た生活扶助 = 生活扶助（ひとり暮らし・20〜40歳・2026年10月から）÷（家賃を除く物価の指数÷100）。大きいほど楽
 2 冬の光熱費        = 電気＋都市ガス＋プロパンガス＋灯油の年額（家計調査・二人以上の世帯）−冬季加算の年額（2人世帯）。小さいほど楽
 3 車なしの暮らしにくさ = ガソリンの年額（家計調査・二人以上の世帯）。生活保護では車を原則持てないので、車に頼る地域ほど不便とみる。小さいほど楽
 4 ごみ袋            = 燃やすごみの指定袋1枚（45リットル換算）。無料の市は0円。小さいほど楽
 5 家賃の上限の余裕   = 住宅扶助の上限（ひとり暮らし）÷（その都道府県の住居の物価の指数÷100）。大きいほど楽
 6 水道代            = 上下水道料の年額（家計調査・二人以上の世帯）。小さいほど楽
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))

ch = load("chiiki.json")
bag = load("gomi_bag.json")["cities"]
kyuchi = {p: dict(v) for p, v in load("kyuchi_by_city.json")["data"].items()}
kijun = load("kijun_r8.json")
keika = load("keika.json")["data"]
jutaku = load("jutaku_limit.json")

LV = ["1級地-1", "1級地-2", "2級地-1", "2級地-2", "3級地-1", "3級地-2"]
AREA = ["", "Ⅰ区", "Ⅱ区", "Ⅲ区", "Ⅳ区", "Ⅴ区", "Ⅵ区"]


def seikatsu_fujo(ages, lv, oct=True):
    """hogohi.html の calcKijun と同じ計算（verify_hogohi.py で厚労省のモデル世帯54通りと一致を確認済みの式）"""
    n = len(ages)
    raw = sum(kijun["dai1"][a][lv] for a in ages)
    d1 = math.ceil(math.floor(round(raw * kijun["teigen"][str(n)] * 1e6) / 1e6) / 10) * 10
    d2 = kijun["dai2"][str(n)]
    per = kijun["tokurei"]["from_2026_10" if oct else "until_2026_09"]
    kei = 0
    for a in ages:
        k = keika[str(n)][a][lv]
        kei += (k - min(1000, k)) if oct else k
    return d1 + d2 + per * n + kei


def jutaku_limit(pref, city, lv, n=1):
    row = jutaku["city"].get(city) or jutaku["pref"][pref][str(lv // 2 + 1)]
    return row[0 if n == 1 else 1 if n == 2 else 2 if n <= 5 else 3 if n == 6 else 4]


def touki_year(pref, n):
    area = str(ch["touki"]["pref_area"].get(pref, 6))
    return ch["touki"]["amount"][area][n - 1] * ch["touki"]["months"][area], int(area)


def rank(values, higher_better):
    """同じ値は同じ順位（平均順位）。1位がいちばん楽"""
    order = sorted(values, key=lambda k: values[k], reverse=higher_better)
    out = {}
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in order[i:j + 1]:
            out[k] = (i + j) / 2 + 1
        i = j + 1
    return out


cities = {}
for c, p in ch["city_pref"].items():
    name = "東京都区部" if c == "東京都区部" else c
    lv = 0 if c == "東京都区部" else kyuchi[p][c]
    k = ch["kakei"][c]
    kon = k["denki"] + k["toshigas"] + k["propane"] + k["toyu"]
    t2, area = touki_year(p, 2)
    t1, _ = touki_year(p, 1)
    fujo = seikatsu_fujo(["20～40"], lv)
    g = ch["gomi"][p].get(c)
    if c == "東京都区部":
        moyasu = "無料"  # 23区は区ごとの答え。17区が無料、4区が一部有料、2区が有料（多く出す家庭などの扱い）。家庭の燃やすごみは基本的に無料
    else:
        moyasu = g["moyasu"]
    if c in bag:
        b = bag[c]
        per45 = round(b["yen"] / b["liters"] * 45, 1)
    else:
        assert moyasu != "有料", c  # 有料と答えた市は値段を調べてある
        per45 = 0.0
    jl = jutaku_limit(p, "東京都" if c == "東京都区部" else c, lv)
    cities[c] = {
        "pref": p, "lv": lv, "lv_name": LV[lv], "area": area, "area_name": AREA[area],
        "fujo": fujo,
        "price": ch["price_city"][c]["yachin_nozoku"],
        "m1": round(fujo / (ch["price_city"][c]["yachin_nozoku"] / 100)),
        "konetsu": kon, "toyu": k["toyu"], "toyu_l": k["toyu_l"], "touki2_year": t2, "touki1_year": t1,
        "m2": kon - t2,
        "m3": k["gasoline"], "bus": k["bus"],
        "m4": per45, "gomi_status": moyasu,
        "jutaku1": jl, "jukyo_idx": ch["price_pref"][p]["jukyo"],
        "m5": round(jl / (ch["price_pref"][p]["jukyo"] / 100)),
        "m6": k["suido"],
    }

MEASURES = {"m1": True, "m2": False, "m3": False, "m4": False, "m5": True, "m6": False}
ranks = {m: rank({c: v[m] for c, v in cities.items()}, hb) for m, hb in MEASURES.items()}
for c, v in cities.items():
    for m in MEASURES:
        v["r" + m[1:]] = ranks[m][c]
total = rank({c: sum(ranks[m][c] for m in MEASURES) for c in cities}, higher_better=False)
for c, v in cities.items():
    v["rank"] = total[c]
    v["rank_sum"] = sum(ranks[m][c] for m in MEASURES)

nat = ch["kakei"]["全国"]
out = {
    "note": "scripts/rank_chiiki.py が作る。物差しの定義はスクリプトの説明を参照。順位は1位がいちばん暮らしやすい。",
    "checked": ch["checked"],
    "national": {"konetsu": nat["denki"] + nat["toshigas"] + nat["propane"] + nat["toyu"], "toyu": nat["toyu"],
                 "gasoline": nat["gasoline"], "suido": nat["suido"]},
    "cities": cities,
}
(ROOT / "data" / "chiiki_rank.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    print("総合順位（暮らしやすい順）")
    for c, v in sorted(cities.items(), key=lambda kv: kv[1]["rank"]):
        print(f'{v["rank"]:>4} {c:<6} {v["lv_name"]} {v["area_name"]} 計{v["rank_sum"]:>5}'
              f' | 物価で見た扶助 {v["m1"]:>6}({v["r1"]:g}) 冬の光熱 {v["m2"]:>7}({v["r2"]:g}) ガソリン {v["m3"]:>6}({v["r3"]:g})'
              f' ごみ袋 {v["m4"]:>5}({v["r4"]:g}) 家賃上限 {v["m5"]:>6}({v["r5"]:g}) 水道 {v["m6"]:>6}({v["r6"]:g})')
