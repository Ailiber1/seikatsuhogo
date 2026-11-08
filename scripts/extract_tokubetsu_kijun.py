"""住宅扶助の「特別基準額」（局長通知 第7の4の(1)のオによる額）の表を data/tokubetsu_kijun.json にする。

引っ越しのときの敷金等の上限は「特別基準額 × 3」（局長通知 第7の4の(1)のカ）。
特別基準額は「1人の限度額 × 人数ごとの率（1人1.3〜7人以上1.8）」で、通知の別表に地域ごとの額がそのまま載っている。
率を自分で掛けると端数がずれる（例: 長崎市 36,000×1.3=46,800 だが表は47,000）ので、表の額をそのまま使う。

元資料: 平成27年4月14日 社援発0414第9号の別表「２ 第７の４の（１）のオによる額」
（写し data/jutaku_limit_2015_source.pdf。jutaku_limit.json と同じ資料）

使い方: python3 scripts/extract_tokubetsu_kijun.py
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
txt = subprocess.run(["pdftotext", "-layout", str(ROOT / "data" / "jutaku_limit_2015_source.pdf"), "-"],
                     capture_output=True, text=True, check=True).stdout
start = txt.index("第７の４の（１）のオによる額")
sec = txt[start:]
yen = r"([\d,]+)円"
pref, city = {}, {}
for line in sec.splitlines():
    m = re.match(r"^\s*(\S+?[都道府県])\s+([１２３123])級地\s+" + r"\s+".join([yen] * 7) + r"\s*$", line)
    if m:
        pref.setdefault(m.group(1), {})[str("１２３123".index(m.group(2)) % 3 + 1)] = [int(v.replace(",", "")) for v in m.groups()[2:]]
        continue
    m = re.match(r"^\s*(\S+?市)\s*(?:政令指定都市|中核市)\s+" + r"\s+".join([yen] * 7) + r"\s*$", line)
    if m:
        city[m.group(1)] = [int(v.replace(",", "")) for v in m.groups()[1:]]

# 照合1: 限度額の表（jutaku_limit.json）と、地域の並びが同じであること
lim = json.loads((ROOT / "data" / "jutaku_limit.json").read_text(encoding="utf-8"))
assert set(pref) == set(lim["pref"]), "都道府県の並びが限度額の表と違う"
assert all(set(pref[p]) == set(lim["pref"][p]) for p in pref), "級地の並びが限度額の表と違う"
assert set(city) == set(lim["city"]), ("市の並びが限度額の表と違う", set(city) ^ set(lim["city"]))

# 照合2: 1人の特別基準額は「1人の限度額×1.3」に近い（表の額は丸めてあるので±1,000円以内）
RATE = [1.3, 1.4, 1.5, 1.6, 1.7, 1.7, 1.8]
far = []
for p, lv in ((p, lv) for p in pref for lv in pref[p]):
    base = lim["pref"][p][lv][0]
    for i, r in enumerate(RATE):
        if abs(pref[p][lv][i] - base * r) > 1000: far.append((p, lv, i + 1, pref[p][lv][i], round(base * r)))
for c in city:
    base = lim["city"][c][0]
    for i, r in enumerate(RATE):
        if abs(city[c][i] - base * r) > 1000: far.append((c, i + 1, city[c][i], round(base * r)))
print("率で計算した額と1,000円より離れている行:", len(far))
for f in far[:10]: print("  ", f)

# 照合3: 公式に出ている数字（東京都1級地・単身 69,800円）
assert pref["東京都"]["1"][0] == 69800
assert city["長崎市"] == [47000, 50000, 54000, 58000, 61000, 61000, 65000]

out = {
    "note": "住宅扶助の特別基準額（局長通知 第7の4の(1)のオ）。値の並びは [1人, 2人, 3人, 4人, 5人, 6人, 7人以上]。"
            "引っ越しの敷金等の上限は、この額×3（局長通知 第7の4の(1)のカ）。pref は都道府県×級地、city は指定都市・中核市（2015年4月時点）。"
            "出典: 平成27年4月14日 社援発0414第9号の別表2（写し data/jutaku_limit_2015_source.pdf）。scripts/extract_tokubetsu_kijun.py が作る",
    "pref": pref, "city": city,
}
(ROOT / "data" / "tokubetsu_kijun.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("都道府県", len(pref), "／都道府県×級地", sum(len(v) for v in pref.values()), "／市", len(city))
