"""hogohi.html の計算式（CALC-START〜CALC-END）を node で実行し、
厚労省 資料4のモデル世帯（data/kijun_r8.json の model_households）と1円単位で一致するか確かめる。

使い方: python3 scripts/verify_hogohi.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "hogohi.html").read_text(encoding="utf-8")
calc = re.search(r"// CALC-START(.*?)// CALC-END", html, re.S).group(1)
kijun = json.loads((ROOT / "data" / "kijun_r8.json").read_text(encoding="utf-8"))
keika = json.loads((ROOT / "data" / "keika.json").read_text(encoding="utf-8"))["data"]

js = calc + f"""
const K = {json.dumps(kijun, ensure_ascii=False)};
const KE = {json.dumps(keika, ensure_ascii=False)};
let ok = 0, ng = [];
for (const m of K.model_households) for (const [lv, [r7, r8]] of Object.entries(m.expect)) {{
  for (const [oct, e] of [[false, r7], [true, r8]]) {{
    const got = calcKijun(m.ages, +lv, oct, K, KE).total;
    if (got === e) ok++; else ng.push([m.name, lv, oct, got, e]);
  }}
}}
console.log(JSON.stringify({{ok, ng}}));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
res = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
total = res["ok"] + len(res["ng"])
print(f"一致 {res['ok']} / {total}")
for row in res["ng"]:
    print("不一致:", row)
sys.exit(0 if not res["ng"] else 1)
