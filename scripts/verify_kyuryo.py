"""kyuryo.html の計算式（CALC-START〜CALC-END）を node で実行し、次を確かめる。

1. 基礎控除額表の全区分で、下限・上限の両端の控除額が表どおりか（全額控除の区分は控除額＝収入）
2. 表の外（231,000円以上）が「4,000円増えるごとに400円加算」になっているか
3. 表の刻みが「19,000円から4,000円ごとに400円」の規則と矛盾しないか（書き写しの誤りを見つけるため）
4. 代表的な例（2万円・5万円・10万円・臨時収入2万円など）が手計算と一致するか

使い方: python3 scripts/verify_kyuryo.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "kyuryo.html").read_text(encoding="utf-8")
calc = re.search(r"// CALC-START(.*?)// CALC-END", html, re.S).group(1)
T = json.loads((ROOT / "data" / "kiso_kojo.json").read_text(encoding="utf-8"))

checks = []
for lo, hi, first, _ in T["rows"]:
    for x in (lo, hi):
        checks.append([f"表 {lo}〜{hi} の {x}円", ["kiso", x], x if first is None else first])
for k in range(0, 6):
    x = 231000 + 4000 * k
    checks.append([f"表の外 {x}円", ["kiso", x], 36400 + 400 * (k + 1)])
    checks.append([f"表の外 {x + 3999}円", ["kiso", x + 3999], 36400 + 400 * (k + 1)])
# 書き写しの確かめ: 19,000円以上は 15,600 + 400×区分番号 になるはず
for lo, hi, first, _ in T["rows"]:
    if lo >= 19000:
        n = (lo - 19000) // 4000
        checks.append([f"刻みの規則 {lo}円", ["const", first], 15600 + 400 * n])
        checks.append([f"区分の幅 {lo}円", ["const", hi - lo], 3999])
examples = [
    ["給料2万円", ["work", 20000, {}], [4400, 15600]],
    ["給料5万円", ["work", 50000, {}], [31600, 18400]],
    ["給料10万円", ["work", 100000, {}], [76400, 23600]],
    ["給料1万5千円", ["work", 15000, {}], [0, 15000]],
    ["給料10万円・天引き1万円", ["work", 100000, {"jippi": 10000}], [66400, 23600]],
    ["給料2万円・新規就労", ["work", 20000, {"shinki": True}], [0, 20000]],
    ["給料5万円・新規就労", ["work", 50000, {"shinki": True}], [18700, 31300]],
    ["臨時収入2万円", ["rinji", 20000, {}], [12000, 8000]],
    ["臨時収入5千円", ["rinji", 5000, {}], [0, 5000]],
]
js = calc + f"""
const T = {json.dumps(T, ensure_ascii=False)};
const checks = {json.dumps(checks, ensure_ascii=False)};
const ex = {json.dumps(examples, ensure_ascii=False)};
let ok = 0; const ng = [];
for (const [name, [type, v], expect] of checks) {{
  const got = type === 'kiso' ? kisoKojo(v, T) : v;
  if (got === expect) ok++; else ng.push([name, got, expect]);
}}
for (const [name, [kind, g, o], [minus, keep]] of ex) {{
  const r = calcIncome(kind, g, o, T);
  if (r.minus === minus && r.keep === keep) ok++; else ng.push([name, [r.minus, r.keep], [minus, keep]]);
}}
console.log(JSON.stringify({{ok, ng}}));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
res = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
print(f"一致 {res['ok']} / {res['ok'] + len(res['ng'])}")
for row in res["ng"]:
    print("不一致:", row)
sys.exit(0 if not res["ng"] else 1)
