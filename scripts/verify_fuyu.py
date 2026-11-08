"""冬の上乗せの解説・ツールを、原本と照合する。

1. 解説の引用（blockquote）が、告示のページ・実施要領の原本PDF（2段組みを左右に分けて読む）・基準部会の資料のどれかにそのままあるか
2. 解説に書いた金額（例の合計・各額）が data/fuyu.json から計算した額と同じか
3. ツールの計算（fuyu.html の CALC 部分）を node で動かし、例の額と同じになるか

使い方: python3 scripts/verify_fuyu.py
"""
import json, re, html, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
norm = lambda s: re.sub(r"\s+", "", s)
ok = ng = 0
def check(c, label):
    global ok, ng
    if c: ok += 1
    else: ng += 1; print("不一致:", label)

def page(name):
    t = (DATA / name).read_text(encoding="utf-8")
    return norm(html.unescape(re.sub(r"<[^>]+>", " ", t)))
def pdf_cols(path):
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
    w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    out = []
    for p in range(1, pages + 1):
        for x in (0, w / 2):
            out.append(subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-x", str(int(x)), "-y", "0", "-W", str(int(w / 2)), "-H", str(int(h)), str(path), "-"],
                                      capture_output=True, text=True).stdout)
    return norm("".join(out))
sources = [page("kokuji158_p4_source.html"), page("kokuji158_p7_source.html"),
           pdf_cols(DATA / "jisshi_yoryo_r8_source.pdf"),
           norm(subprocess.run(["pdftotext", str(DATA / "kijunbukai63_shiryo1_source.pdf"), "-"], capture_output=True, text=True).stdout)]

doc = (ROOT / "fuyu-setsumei.html").read_text(encoding="utf-8")
for q in re.findall(r"<blockquote>(.*?)</blockquote>", doc, re.S):
    q = norm(html.unescape(re.sub(r"<[^>]+>", "", q)))
    check(any(q in s for s in sources), "引用が原本にない: " + q[:40])

f = json.loads((DATA / "fuyu.json").read_text(encoding="utf-8"))
kyuchi = json.loads((DATA / "kyuchi_by_city.json").read_text(encoding="utf-8"))["data"]
lv = lambda p, c: dict(kyuchi[p])[c]
def total(p, c, n=1):
    a = str(f["pref_area"].get(p, 6)); t = f["touki"][a][n - 1]; k = f["kimatsu"][lv(p, c)][n - 1]
    return t, k, t * f["months"][a] + k
EXPECT = {("北海道", "札幌市"): 103310, ("長崎県", "長崎市"): 26340, ("東京都", "千代田区"): 27650}
for (p, c), want in EXPECT.items():
    check(total(p, c)[2] == want, f"{c} の冬の合計")
    check(f"{want:,}" in doc or c == "千代田区", f"{c} の合計 {want:,} が解説にない")
t, k, _ = total("長崎県", "長崎市")
for s in [f"{t:,}円 × 11月〜3月の5か月 ＝ {t * 5:,}円", f"12月に {k:,}円", f"{t + k:,}円の上乗せ"]:
    check(s in doc, "長崎市の内訳が解説にない: " + s)
check(min(r[0] for r in f["kimatsu"]) == 11240 and max(r[0] for r in f["kimatsu"]) == 14500 and "11,240円〜14,500円" in doc, "期末一時扶助の幅")
check(f["kimatsu_before"][0][0] == 14160 and f["kimatsu_before"][2][0] == 12880 and "14,160円→14,500円" in doc and "12,880円→13,190円" in doc, "改正前後の額")
for s in ["28,201", "24,769", "17,318"]:
    check(s in doc and s in sources[3], "基準部会の数字: " + s)

# 3. ツールの計算を node で動かす
tool = (ROOT / "fuyu.html").read_text(encoding="utf-8")
calc = tool[tool.index("// CALC-START"):tool.index("// CALC-END")]
fjs = re.search(r"const F = (\{.*?\});\n", tool).group(1)
js = f"const F = {fjs};\n{calc}\n" + "console.log(JSON.stringify([calcFuyu('北海道',1,1).total, calcFuyu('長崎県',2,1).total, calcFuyu('東京都',0,1).total, calcFuyu('東京都',0,12).total]));"
res = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
check(res[:3] == [103310, 26340, 27650], f"ツールの計算 {res[:3]}")
a6 = f["touki"]["6"]; k0 = f["kimatsu"][0]
check(res[3] == (a6[8] + a6[9] * 3) * 5 + (k0[8] + k0[9] * 3), "ツールの10人以上の計算")
print(f"照合: 一致 {ok} 件 / 不一致 {ng} 件")
if ng: raise SystemExit(1)
