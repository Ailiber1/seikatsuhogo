"""北九州市「不正受給の状況」のページから、年度ごとの件数・金額・内容・発見の契機を取り出して
data/kitakyushu_fusei.json を作る。

使い方: python3 scripts/extract_kitakyushu.py
取り出した表は、合計と小計が合うかを確かめてから書き出す（合わなければ止まる）。
これは北九州市1市の数字で、全国の数字ではない。
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://www.city.kitakyushu.lg.jp/contents/19200019.html"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "kitakyushu_fusei.json"

raw = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read().decode("utf-8", "ignore")
raw = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", raw)
text = html.unescape(re.sub(r"<[^>]+>", "\n", raw))
lines = [l.strip() for l in text.splitlines() if l.strip()]

updated = re.search(r"更新日\s*:\s*(\d{4})年(\d{1,2})月(\d{1,2})日", "\n".join(lines))
if not updated:
    sys.exit("更新日が見つからない")
updated_s = "%04d-%02d-%02d" % tuple(int(x) for x in updated.groups())

YEARS = ["平成30年度", "令和元年度", "令和2年度", "令和3年度", "令和4年度", "令和5年度", "令和6年度", "令和7年度"]


def section(start, end):
    i = lines.index(start)
    j = lines.index(end, i + 1)
    return lines[i + 1:j]


def num(s):
    return int(re.sub(r"[^\d]", "", s))


# 1 件数と金額
s1 = section("1　不正受給の件数と金額", "2　不正の内容と件数")
count_amount = {}
k = 0
while k < len(s1):
    if s1[k] in YEARS:
        count_amount[s1[k]] = {"count": num(s1[k + 1]), "amount": num(s1[k + 2])}
        k += 3
    else:
        k += 1
if list(count_amount) != YEARS:
    sys.exit("件数と金額の年度が足りない: %s" % list(count_amount))


def rows_after_years(sec):
    # 年度見出しが並んだあと、「ラベル → 数字8個」を順に読む
    k = 0
    while k < len(sec) and sec[k] != YEARS[-1]:
        k += 1
    k += 1
    out = []
    label = None
    nums = []
    skip = {"稼働収入", "稼働収入以外", "の収入", "扶助費の不正", "その他", "重複受給"}
    while k < len(sec):
        t = sec[k]
        if re.fullmatch(r"[\d,]+", t):
            nums.append(num(t))
            if len(nums) == 8:
                out.append((label, nums))
                label, nums = None, []
        else:
            if nums:
                sys.exit("数字が8個にならない: %s %s" % (label, nums))
            label = t if label is None else label + " " + t
        k += 1
    return out


s2 = section("2　不正の内容と件数", "3　不正受給発見の契機")
r2 = rows_after_years(s2)
s3 = section("3　不正受給発見の契機", "4　刑事罰の状況")
r3 = rows_after_years(s3)

# ラベルを整える（ページの見出し行のずれを吸収する）
kinds = {}
order2 = ["稼働収入の無申告", "稼働収入の過少申告", "稼働収入 小計", "労災補償金等の無申告", "任意保険金等の無申告",
          "各種年金及び福祉各法に基づく給付の無申告", "預貯金等の無申告", "資産収入の無申告", "交通事故に係る収入の無申告",
          "稼働収入以外 その他", "稼働収入以外 小計", "住宅扶助", "扶助費 その他（移送費など）", "扶助費 小計",
          "重複受給", "世帯員の増減・転居の無届", "その他 その他", "その他 小計", "合計"]
if len(r2) != len(order2):
    sys.exit("内容の行数が合わない: %d" % len(r2))
for (_, nums), name in zip(r2, order2):
    kinds[name] = nums

order3 = ["住民等からの通報・投書", "関係機関からの通報・照会", "監査及び検査の指摘", "課税状況調査", "福祉事務所の調査", "その他", "合計"]
if len(r3) != len(order3):
    sys.exit("契機の行数が合わない: %d" % len(r3))
trigger = {name: nums for (_, nums), name in zip(r3, order3)}

# 検算
tot = [count_amount[y]["count"] for y in YEARS]
assert kinds["合計"] == tot, "内容の合計が件数と違う"
assert trigger["合計"] == tot, "契機の合計が件数と違う"
for i in range(8):
    assert kinds["稼働収入の無申告"][i] + kinds["稼働収入の過少申告"][i] == kinds["稼働収入 小計"][i]
    s_other = sum(kinds[n][i] for n in order2[3:10])
    assert s_other == kinds["稼働収入以外 小計"][i], ("稼働収入以外", i)
    assert kinds["住宅扶助"][i] + kinds["扶助費 その他（移送費など）"][i] == kinds["扶助費 小計"][i]
    assert sum(kinds[n][i] for n in order2[14:17]) == kinds["その他 小計"][i], ("その他", i)
    assert kinds["稼働収入 小計"][i] + kinds["稼働収入以外 小計"][i] + kinds["扶助費 小計"][i] + kinds["その他 小計"][i] == tot[i]

# 発見の契機は、ページ自体の合計が内訳の和と合わない年度がある（令和2年度は内訳の和267、合計269）。
# 勝手に直さず、合わない年度を記録して、資料では合う年度だけを使う
trigger_mismatch = {YEARS[i]: {"sum": sum(trigger[n][i] for n in order3[:6]), "total": tot[i]}
                    for i in range(8) if sum(trigger[n][i] for n in order3[:6]) != tot[i]}
if trigger_mismatch:
    print("注意: 発見の契機の合計が内訳の和と合わない年度:", trigger_mismatch)

OUT.write_text(json.dumps({
    "source": {"title": "北九州市「不正受給の状況」", "url": URL, "updated": updated_s},
    "note": "北九州市1市の数字。全国の数字ではない",
    "years": YEARS, "count_amount": count_amount, "kinds": kinds, "trigger": trigger,
    "trigger_sum_mismatch": trigger_mismatch,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("書き出しました:", OUT, "更新日", updated_s)
print("令和7年度 合計", tot[-1], "稼働収入 小計", kinds["稼働収入 小計"][-1], "契機: 福祉事務所", trigger["福祉事務所の調査"][-1], "課税", trigger["課税状況調査"][-1], "通報", trigger["住民等からの通報・投書"][-1])
