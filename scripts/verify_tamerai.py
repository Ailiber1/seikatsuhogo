"""tamerai.html の計算を node で動かして確かめる。

1. 生活扶助の計算（CALC-START〜CALC-END）が hogohi.html と同じで、厚労省 資料4のモデル世帯54件と1円単位で一致するか
2. 残せる額の判定（KEEP-START〜KEEP-END）が chokin.html と同じか
3. 線より下かどうかの分け方（LINE-START〜LINE-END）が、国の推計と同じ分け方（収入＜最低生活費／貯金＜最低生活費1か月分）になっているか
4. 資料（hosoku-setsumei.html）とツールに書いた割合・件数が、data/hosoku.json と合っているか

使い方: python3 scripts/verify_tamerai.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
read = lambda name: (ROOT / name).read_text(encoding="utf-8")
html = read("tamerai.html")
grab = lambda src, tag: re.search(rf"// {tag}-START(.*?)// {tag}-END", src, re.S).group(1)
calc, keep, line = grab(html, "CALC"), grab(html, "KEEP"), grab(html, "LINE")
if calc != grab(read("hogohi.html"), "CALC"):
    sys.exit("生活扶助の計算が hogohi.html と違います")
if keep != grab(read("chokin.html"), "KEEP"):
    sys.exit("残せる額の判定が chokin.html と違います")

kijun = json.loads(read("data/kijun_r8.json"))
keika = json.loads(read("data/keika.json"))["data"]
js = calc + keep + line + f"""
const K = {json.dumps(kijun, ensure_ascii=False)};
const KE = {json.dumps(keika, ensure_ascii=False)};
let ok = 0, ng = [];
for (const m of K.model_households) for (const [lv, [r7, r8]] of Object.entries(m.expect)) {{
  for (const [oct, e] of [[false, r7], [true, r8]]) {{
    const got = calcKijun(m.ages, +lv, oct, K, KE).total;
    if (got === e) ok++; else ng.push([m.name, lv, oct, got, e]);
  }}
}}
// 分け方の境目: 収入が線ちょうどなら「線以上」／1円少なければ線より下。貯金が1か月分ちょうどなら「収入だけ」側
const cases = [[100000, 100000, 0, 'above', 0], [100000, 99999, 0, 'both', 1], [100000, 0, 99999, 'both', 100000],
               [100000, 0, 100000, 'income', 100000], [100000, 50000, 300000, 'income', 50000], [100000, 120000, 0, 'above', -20000]];
const bad = cases.filter(([m, i, x, p, g]) => {{ const r = judgeLine(m, i, x); return r.pos !== p || r.gap !== g; }});
console.log(JSON.stringify({{ok, ng, bad}}));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
res = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
print(f"生活扶助のモデル世帯: 一致 {res['ok']} / {res['ok'] + len(res['ng'])}")
for row in res["ng"]:
    print("不一致:", row)
print("線より下かどうかの分け方の境目:", "すべて正しい" if not res["bad"] else res["bad"])

# 4. ページに書いた数字が data/hosoku.json と合っているか
d = json.loads(read("data/hosoku.json"))
doc = read("hosoku-setsumei.html")
h = d["hihogosha_2026_07"]
need = {
    "hosoku-setsumei.html": ["22.6%", "43.7%", "15.3%", "32.1%", f"{h['applications']:,}件", f"{h['started']:,}世帯",
                             "196万9,655人", "164万4,102世帯", f"data-w=\"{h['started'] / h['applications'] * 100:.1f}\""],
    "tamerai.html": ["22.6%", "43.7%"],
}
miss = [(p, s) for p, arr in need.items() for s in arr if s not in read(p)]
assert h["persons"] == 1969655 and h["households"] == 1644102
quotes = [e["quote"] for e in d["estimates"] if "quote" in e] + [d["estimates"][0]["caveat"]]
miss += [("hosoku-setsumei.html（引用）", q[:20]) for q in quotes if q not in doc]
miss += [("tamerai.html（引用）", r["q"][:20]) for r in d["reasons"] if r["q"] not in html]
print("ページの数字・引用と data/hosoku.json:", "すべて一致" if not miss else miss)
sys.exit(0 if not res["ng"] and not res["bad"] and not miss else 1)
