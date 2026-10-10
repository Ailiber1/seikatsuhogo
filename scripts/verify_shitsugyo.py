"""shitsugyo.html（失業・低収入チェック）の計算を確かめる。

1. data/shitsugyo.json の給付日数の表が、ハローワークのページの写し（data/hellowork_benefitdays_source.html）の表と一致するか
   （rowspan・colspan を展開して読み直す）
2. 生活扶助の計算（CALC）が hogohi.html と、基礎控除（kisoKojo）が kyuryo.html と同じか
3. 1日の額の計算式が、厚労省の上限額・下限額（令和8年8月1日から）と一致し、区切りの前後で途切れないか
4. 日数の判定（辞めた理由×年齢×期間）と、低収入の計算の例

使い方: python3 scripts/verify_shitsugyo.py
"""
import html as H, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
page = (ROOT / "shitsugyo.html").read_text(encoding="utf-8")
grab = lambda src, tag: re.search(rf"// {tag}-START(.*?)// {tag}-END", src, re.S).group(1)
S = json.loads((ROOT / "data" / "shitsugyo.json").read_text(encoding="utf-8"))
K = S["kihon"]
errors = []

# 1. 日数の表をハローワークの写しから読み直す
src = (ROOT / "data" / "hellowork_benefitdays_source.html").read_text(encoding="utf-8", errors="replace")
def expand(table):
    grid, spans = [], {}
    for r, tr in enumerate(re.findall(r"<tr.*?</tr>", table, re.S)):
        row, c = [], 0
        cells = re.findall(r"<t[hd]([^>]*)>(.*?)</t[hd]>", tr, re.S)
        for attrs, body in cells:
            while (r, c) in spans: row.append(spans.pop((r, c))); c += 1
            rs = int((re.search(r'rowspan="(\d+)"', attrs) or [0, 1])[1]); cs = int((re.search(r'colspan="(\d+)"', attrs) or [0, 1])[1])
            text = re.sub(r"\s+", "", H.unescape(re.sub(r"<[^>]+>", "", body)))
            for j in range(cs):
                row.append(text)
                for i in range(1, rs): spans[(r + i, c + j)] = text
            c += cs
        while (r, c) in spans: row.append(spans.pop((r, c))); c += 1
        grid.append(row)
    return grid
tables = [expand(t) for t in re.findall(r"<table.*?</table>", src, re.S)]
days = lambda t: None if t == "―" else int(re.sub(r"[^\d]", "", t))
t1 = {row[1]: [days(x) for x in row[2:7]] for row in tables[0][2:]}
t2 = {row[1]: [days(x) for x in row[2:7]] for row in tables[1][2:]}
for age in K["ages"]:
    if t1.get(age) != K["days_tokutei"][age]: errors.append(f"特定受給資格者の表が違う: {age} 写し{t1.get(age)} / json{K['days_tokutei'][age]}")
if t2.get("全年齢") != K["days_ippan"]["全年齢"]: errors.append(f"一般の表が違う: 写し{t2.get('全年齢')} / json{K['days_ippan']['全年齢']}")
print("給付日数の表（ハローワークの写しと照合）:", "一致" if not errors else "不一致あり")

# 2. ほかのツールと同じ計算か
if grab(page, "CALC") != grab((ROOT / "hogohi.html").read_text(encoding="utf-8"), "CALC"):
    errors.append("生活扶助の計算が hogohi.html と違います")
fn = lambda s: re.search(r"function kisoKojo.*?\n}\n", s, re.S).group(0)
if fn(page) != fn((ROOT / "kyuryo.html").read_text(encoding="utf-8")):
    errors.append("基礎控除の計算が kyuryo.html と違います")

# 3・4. node で計算式を動かす
kiso = json.loads((ROOT / "data" / "kiso_kojo.json").read_text(encoding="utf-8"))
js = grab(page, "KISO") + grab(page, "KIHON") + grab(page, "LOW") + f"""
const K = {json.dumps(K, ensure_ascii=False)};
const T = {json.dumps(kiso, ensure_ascii=False)};
const out = {{}};
// 上限額・下限額（厚労省「基本手当日額の計算式及び金額(令和8年8月1日～)」）
out.caps = [0,1,3,4].map(a => [kihonDaily(K.nichigaku.bands[AGE_PAY[a]].cap_w, a, K), kihonDaily(99999, a, K)]);
out.low = [0,1,3,4].map(a => kihonDaily(1000, a, K));
// 区切りの前後で途切れないか（1円刻みで、隣との差が2円を超えない）
out.jump = [];
for (const a of [0,1,3,4]) for (let w = 3203; w <= 20000; w++) {{
  const d = kihonDaily(w + 1, a, K) - kihonDaily(w, a, K);
  if (d < -1 || d > 2) out.jump.push([a, w, d]);
}}
out.ex = [kihonDaily(10000, 1, K), kihonDaily(12120, 4, K), kihonDaily(5000, 0, K)];
out.days = [
  kihonDays('tosan', 3, 5, K), kihonDays('jiko', 2, 3, K), kihonDays('jiko', 2, 1, K), kihonDays('kibou', 1, 1, K),
  kihonDays('keiyaku', 0, 4, K), kihonDays('byoki_ng', 0, 0, K), kihonDays('kaiko', 5, 3, K), kihonDays('tosan', 0, 5, K)
];
out.lowEx = lowIncome(109930, 170000, 140000, T);
console.log(JSON.stringify(out));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
r = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)

expect_caps = [[7450, 7450], [8270, 8270], [9110, 9110], [7830, 7830]]
if r["caps"] != expect_caps: errors.append(f"上限額が違う: {r['caps']}")
if r["low"] != [2562] * 4: errors.append(f"下限額が違う: {r['low']}")
if r["jump"]: errors.append(f"計算式が途切れる所: {r['jump'][:5]}")
print("1日の額: 上限", [c[0] for c in r["caps"]], "下限", r["low"][0], "／ 区切りの前後:", "なめらか" if not r["jump"] else "途切れあり")
# 例: 30〜44歳・賃金日額1万円 = 0.8×10000 − 0.3×(4520/8010)×10000 = 6,307.1… → 6,307円
#     60〜64歳・12,120円 = 0.45×12120 = 5,454円（2つの式が同じ値）／ 29歳以下・5,000円 = 4,000円
if r["ex"] != [6307, 5454, 4000]: errors.append(f"計算例が違う: {r['ex']}")
print("計算例（6,307・5,454・4,000円）:", r["ex"])

want = [("ok", 330, 0), ("ok", 90, 1), ("short", None, None), ("ok", 90, 0), ("ok", 180, 0), ("cannot", None, None), ("over65", None, None), ("invalid", None, None)]
labels = ["倒産・45〜59歳・20年以上", "自己都合・35〜44歳・5〜10年", "自己都合・35〜44歳・6か月〜1年", "希望退職・30〜34歳・6か月〜1年",
          "契約更新なし・29歳以下・10〜20年", "病気で働けない", "解雇・65歳以上", "倒産・29歳以下・20年以上（表は―）"]
for lab, got, (k, d, wm) in zip(labels, r["days"], want):
    ok = got["kind"] == k and (d is None or got.get("days") == d) and (wm is None or got.get("waitMonths") == wm)
    print(f"  {'✓' if ok else '✗'} {lab}: {got}")
    if not ok: errors.append(f"日数の判定: {lab}")
print("低収入の例（基準109,930円・総支給17万・手取り14万）:", r["lowEx"])

if errors:
    print("\n".join("NG: " + e for e in errors)); sys.exit(1)
print("すべて確認できました")
