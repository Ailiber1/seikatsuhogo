"""chiiki.html（住む場所の暮らしやすさしらべ）と chiiki-setsumei.html を確かめる。

使い方: python3 scripts/verify_chiiki.py
1. ツールの生活扶助の計算式が hogohi.html（厚労省のモデル世帯54通りと一致を確認済み）と1文字も違わない
2. ツールの計算（node で実行）が、rank_chiiki.py の生活扶助と、全年齢×全級地で一致する
3. ツールの52都市ランキング（物差し6つ・総合）が、rank_chiiki.py の順位と全都市で一致する
4. 資料に、差し込み忘れ・NaN・undefined が残っていない。結論の1位・52位が順位表と合っている
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rank_chiiki as rk

ROOT = Path(__file__).resolve().parent.parent
tool = (ROOT / "chiiki.html").read_text(encoding="utf-8")
hogohi = (ROOT / "hogohi.html").read_text(encoding="utf-8")
doc = (ROOT / "chiiki-setsumei.html").read_text(encoding="utf-8")
ng = []

calc = lambda s: s.split("// CALC-START")[1].split("// CALC-END")[0]
if calc(tool) != calc(hogohi):
    ng.append("生活扶助の計算式が hogohi.html と違う")

start = tool.index("const KYUCHI")
end = tool.index("// RANK-END")
js = tool[start:end] + """
const AG = ["18～19","20～40","41～59","60～64","65～69","70～74","75～"];
const fujo = {};
AG.forEach(a => { fujo[a] = [0,1,2,3,4,5].map(lv => calcKijun([a], lv, true, KIJUN, KEIKA).total); });
const all = ranking52(MEAS.map(m => m.k));
console.log(JSON.stringify({fujo, per: all.per, total: all.total}));
"""
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
res = json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout)
Path(f.name).unlink()

n_fujo = 0
for a, vals in res["fujo"].items():
    for lv, v in enumerate(vals):
        n_fujo += 1
        if v != rk.seikatsu_fujo([a], lv):
            ng.append(f"生活扶助が違う {a} {rk.LV[lv]} ツール{v} python{rk.seikatsu_fujo([a], lv)}")
if res["fujo"]["20～40"][0] != 77220:
    ng.append("1級地-1・20〜40歳・ひとり暮らしが 77,220円 でない")

R = json.loads((ROOT / "data" / "chiiki_rank.json").read_text(encoding="utf-8"))["cities"]
n_rank = 0
for c, v in R.items():
    for k in range(1, 7):
        n_rank += 1
        if res["per"]["m" + str(k)][c] != v["r" + str(k)]:
            ng.append(f"物差し{k}の順位が違う {c}")
    n_rank += 1
    if res["total"][c] != v["rank"]:
        ng.append(f"総合順位が違う {c} ツール{res['total'][c]} python{v['rank']}")

if "%%" in doc:
    ng.append("資料に差し込み忘れ（%%）がある")
for bad in ("NaN", "undefined"):
    if bad in doc:
        ng.append(f"資料に {bad} がある")
top = min(R, key=lambda c: R[c]["rank"])
last = max(R, key=lambda c: R[c]["rank"])
concl = doc.split('class="conclusion"')[1].split("</p></div>")[0]
if top not in concl or last not in concl:
    ng.append("結論の1位・52位が順位表と合わない")
for ph in re.findall(r"/\*[A-Z0-9]+\*/", tool):
    ng.append(f"ツールに差し込み忘れ {ph}")

print(f"生活扶助 {n_fujo}通り・順位 {n_rank}件を確かめました")
if ng:
    print("合わないところ:")
    for x in ng:
        print(" -", x)
    sys.exit(1)
print("すべて一致しました")
