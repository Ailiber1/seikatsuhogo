"""冬の上乗せ（冬季加算・期末一時扶助）のデータを公的資料から読み取り、data/fuyu.json を作る。

読むもの（写しは data/ にある）
1. 生活保護法による保護の基準（昭和38年厚生省告示第158号）厚労省 法令等データベース 2026年11月8日取得
   p4: 別表第1 第1章1 居宅の第2類（地区別冬季加算額）と期末一時扶助費の表  data/kokuji158_p4_source.html
   p7: 冬季加算のⅠ区〜Ⅵ区の都道府県の区分                                  data/kokuji158_p7_source.html
   https://www.mhlw.go.jp/web/t_doc?dataId=82051000&dataType=0&pageNo=4 （pageNo=7）
2. 改正前の期末一時扶助（2026年3月まで）: 厚労省「2026（令和8）年4月1日施行 生活保護実施要領等」の告示の新旧対照表
   data/jisshi_yoryo_r8_source.pdf  https://www.mhlw.go.jp/content/001677054.pdf
3. 第63回 社会保障審議会生活保護基準部会（2026年11月5日）資料1 data/kijunbukai63_shiryo1_source.pdf
   https://www.mhlw.go.jp/content/12002000/001766052.pdf （議事次第 data/kijunbukai63_shidai_source.pdf）

使い方: python3 scripts/extract_fuyu.py
"""
import json, re, html, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
num = lambda s: int(s.replace(",", "").replace("円", ""))

def page(name):
    t = (DATA / name).read_text(encoding="utf-8")
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)

p4, p7 = page("kokuji158_p4_source.html"), page("kokuji158_p7_source.html")
AREAS = ["Ⅰ", "Ⅱ", "Ⅲ", "Ⅳ", "Ⅴ", "Ⅵ"]
N = r"([\d,]+円?)"

# 1. 冬季加算（居宅）：第2類の表の中の「地区別冬季加算額」。1〜5人の表と、6〜9人・10人以上1人ごとの表の2つ
sec = p4[p4.index("第2類 基準額及び加算額"):p4.index("(2) 基準生活費の算定")]
first, second = sec.split("基準額及び加算額 世帯人員別 6人")
touki, period = {}, {}
for i, a in enumerate(AREAS, 1):
    m1 = re.search(a + r"区\((\d+)月から(\d+)月まで\) " + " ".join([N] * 5), first)
    m2 = re.search(a + r"区\((\d+)月から(\d+)月まで\) " + " ".join([N] * 5), second)
    touki[str(i)] = [num(v) for v in m1.groups()[2:]] + [num(v) for v in m2.groups()[2:]]  # 1〜9人, 10人以上1人ごとの額
    period[str(i)] = [int(m1.group(1)), int(m1.group(2))]
months = {k: (e - s + 12) % 12 + 1 for k, (s, e) in period.items()}

# 2. 期末一時扶助（12月）：級地ごと
LV = ["1級地―1", "1級地―2", "2級地―1", "2級地―2", "3級地―1", "3級地―2"]
ks = p4.index("期末一時扶助費 級地別")
ksec = p4[ks:p4.index("経過的加算額(月額)", ks)]
k1, k2 = ksec.split("1人を増すごとに加算する額")
kimatsu = []
for lv in LV:
    a = re.search(lv + " " + " ".join([N] * 5), k1).groups()
    b = re.search(lv + " " + " ".join([N] * 5), k2).groups()
    kimatsu.append([num(v) for v in a + b])  # 1〜9人, 10人以上1人ごとの額

# 3. 地区の区分（都道府県）
asec = p7[p7.index("地区別 Ⅰ区 Ⅱ区"):p7.index("その他の都府県")]
names = asec.split("都道府県名")[1].split()
group_sizes = [3, 3, 4, 2, 6]  # Ⅰ区〜Ⅴ区の並び（原文の表の列の順に、北海道 青森県 秋田県｜岩手県…）
pref_area, k = {}, 0
for i, size in enumerate(group_sizes, 1):
    for nm in names[k:k + size]: pref_area[nm] = i
    k += size
assert k == len(names), names

# 照合: 地域差の回（data/chiiki.json）で使った冬季加算と同じか
ch = json.loads((DATA / "chiiki.json").read_text(encoding="utf-8"))["touki"]
assert all(touki[a][:5] == ch["amount"][a] for a in touki), "chiiki.json と冬季加算の額が違う"
assert pref_area == ch["pref_area"], "chiiki.json と地区の区分が違う"
assert all(months[a] == ch["months"][a] for a in months), "月数が違う"

# 4. 改正前の期末一時扶助（新旧対照表の右側）
yoryo = subprocess.run(["pdftotext", "-layout", "-f", "1", "-l", "12", str(DATA / "jisshi_yoryo_r8_source.pdf"), "-"],
                       capture_output=True, text=True, check=True).stdout
before = {}
for line in yoryo.splitlines():
    m = re.match(r"^\s*([１２３])級地－([１２])\s+" + r"\s+".join([N] * 5) + r"\s+([１２３])級地－([１２])\s+" + r"\s+".join([N] * 5) + r"\s*$", line)
    if m:
        g = m.groups()
        key = f"{'１２３'.index(g[0]) + 1}級地―{'１２'.index(g[1]) + 1}"
        if key in before: continue  # 2回目に出てくる同じ級地の行は6人以上の表
        after = [num(v) for v in g[2:7]]
        before[key] = [num(v) for v in g[9:14]]
        assert after == kimatsu[LV.index(key)][:5], ("新旧対照表の改正後と告示が違う", key)
assert len(before) == 6, before

# 5. 基準部会（2026年11月5日）の数字
bk = re.sub(r"\s+", "", subprocess.run(["pdftotext", str(DATA / "kijunbukai63_shiryo1_source.pdf"), "-"],
                                        capture_output=True, text=True, check=True).stdout)
for s in ["28,201", "24,769", "17,318", "約７割", "Ⅵ区において冬季の加算対象月は１ヶ月短縮する"]:
    assert s in bk, s

out = {
    "note": "冬の上乗せ。touki は居宅の地区別冬季加算額（月額）で並びは [1〜9人, 10人以上1人ごとの額]、period は [始まる月, 終わる月]。"
            "kimatsu は期末一時扶助費（12月に1回）で、級地 [1級地-1, 1級地-2, 2級地-1, 2級地-2, 3級地-1, 3級地-2] ごとに [1〜9人, 10人以上1人ごとの額]。"
            "kimatsu_before は2026年3月までの額（1〜5人）。出典は scripts/extract_fuyu.py の説明。確認日 2026-11-08",
    "touki": touki, "period": period, "months": months, "pref_area": pref_area,
    "kimatsu": kimatsu, "kimatsu_before": [before[lv] for lv in LV],
    "bukai": {"date": "2026-11-05", "dec_extra_total": 28201, "dec_extra_no_kounetsu": 24769, "dec_extra_food": 17318, "food_share": "約7割",
              "note": "2人以上世帯・年収階級第1十分位、家計調査2021〜2025年の特別集計。12月と10〜11月平均の差"},
}
(DATA / "fuyu.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("冬季加算", {a: (period[a], touki[a][0]) for a in touki})
print("期末一時扶助 1人", [r[0] for r in kimatsu], "／改正前", [r[0] for r in out["kimatsu_before"]])
print("地区の区分", len(pref_area), "都道府県（他はⅥ区）")
