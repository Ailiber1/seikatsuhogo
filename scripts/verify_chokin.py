"""chokin.html の計算を node で動かして確かめる。

1. 生活扶助の計算（CALC-START〜CALC-END）が hogohi.html と同じで、厚労省 資料4のモデル世帯54件と1円単位で一致するか
2. 残せる額の判定（KEEP-START〜KEEP-END）が「最低生活費の5割まで残せる・超えた分を差し引く」になっているか
3. 長崎市・単身・20〜40歳（配信者本人）の最低生活費と、残せる額

使い方: python3 scripts/verify_chokin.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
html = (ROOT / "chokin.html").read_text(encoding="utf-8")
grab = lambda src, tag: re.search(rf"// {tag}-START(.*?)// {tag}-END", src, re.S).group(1)
calc, keep = grab(html, "CALC"), grab(html, "KEEP")
if calc != grab((ROOT / "hogohi.html").read_text(encoding="utf-8"), "CALC"):
    sys.exit("生活扶助の計算が hogohi.html と違います")

kijun = json.loads((ROOT / "data" / "kijun_r8.json").read_text(encoding="utf-8"))
keika = json.loads((ROOT / "data" / "keika.json").read_text(encoding="utf-8"))["data"]
jutaku = json.loads((ROOT / "data" / "jutaku_limit.json").read_text(encoding="utf-8"))
nagasaki_lv = next(lv for p, rows in json.loads((ROOT / "data" / "kyuchi_by_city.json").read_text(encoding="utf-8"))["data"].items()
                   for nm, lv in rows if p == "長崎県" and nm == "長崎市")

js = calc + keep + f"""
const K = {json.dumps(kijun, ensure_ascii=False)};
const KE = {json.dumps(keika, ensure_ascii=False)};
let ok = 0, ng = [];
for (const m of K.model_households) for (const [lv, [r7, r8]] of Object.entries(m.expect)) {{
  for (const [oct, e] of [[false, r7], [true, r8]]) {{
    const got = calcKijun(m.ages, +lv, oct, K, KE).total;
    if (got === e) ok++; else ng.push([m.name, lv, oct, got, e]);
  }}
}}
// 判定の境目: 半分ちょうどは残せる／1円超えると差し引き／1か月分ちょうどからは「1か月分以上」
const cases = [[100000, 0, 'ok', 0], [100000, 50000, 'ok', 0], [100000, 50001, 'cut', 1], [100000, 99999, 'cut', 49999],
               [100000, 100000, 'over', 50000], [108931, 54465, 'ok', 0], [108931, 54466, 'cut', 1]];
const bad = cases.filter(([m, x, k, c]) => {{ const r = judgeMoney(m, x); return r.kind !== k || r.cut !== c; }});
const life = calcKijun(['20～40'], {nagasaki_lv}, true, K, KE).total, life9 = calcKijun(['20～40'], {nagasaki_lv}, false, K, KE).total;
console.log(JSON.stringify({{ok, ng, bad, life, life9}}));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
res = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
print(f"生活扶助のモデル世帯: 一致 {res['ok']} / {res['ok'] + len(res['ng'])}")
for row in res["ng"]:
    print("不一致:", row)
print("残せる額の判定の境目:", "すべて正しい" if not res["bad"] else res["bad"])
rent = jutaku["city"]["長崎市"][0]
for label, life in (("10月から", res["life"]), ("9月まで", res["life9"])):
    m = life + rent
    print(f"長崎市・単身・20〜40歳（{label}）: 生活扶助 {life:,}円＋家賃の上限 {rent:,}円＝{m:,}円 → 残せる {m // 2:,}円")
sys.exit(0 if not res["ng"] and not res["bad"] else 1)
