"""止まるラインの解説（teishi-setsumei.html）とツール（teishi.html）を、data/ から生成する。

使い方:
  python3 scripts/extract_teishi_law.py   # 生活保護法 第8条・第26条を取得（条文が変わったときだけ）
  python3 scripts/gen_teishi.py
  python3 scripts/verify_teishi.py        # 引用・計算・金額を原本と照合する

ツールの CALC-START〜CALC-END の計算を、解説にも同じものとして埋め込む（計算の正本は1か所）。
解説の本文にある金額（{{...}}）は、その計算を node で動かして差し込む。
"""
import json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
yen = lambda n: f"{n:,}"

kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
jutaku = {k: v for k, v in load("jutaku_limit.json").items() if k in ("pref", "city", "later_core_cities")}
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}
kiso = {k: v for k, v in load("kiso_kojo.json").items() if k in ("rows", "over")}

tool = (ROOT / "scripts" / "teishi.template.html").read_text(encoding="utf-8")
calc = re.search(r"// CALC-START\n(.*?)// CALC-END", tool, re.S).group(1)

# --- 解説の例（ひとり暮らし・20〜40歳・天引きなし）を、ツールと同じ計算で出す ---
EX = [["札幌市", "北海道", "札幌市"], ["長崎市", "長崎県", "長崎市"], ["東京23区", "東京都", "千代田区"]]
EX_AGES = ["20～40"]
lv_of = lambda p, c: dict(kyuchi[p])[c]
js = calc + f"""
const KE = {dump(keika)}, K = {dump(kijun)}, J = {dump(jutaku)}, T = {dump(kiso)};
const ex = {dump(EX)};
const KY = {dump({p: dict(v) for p, v in kyuchi.items() if p in ('北海道', '長崎県', '東京都')})};
const out = ex.map(([nm, p, c]) => {{
  const lv = KY[p][c], life = calcKijun({dump(EX_AGES)}, lv, true, K, KE).total, lim = jutakuLimit(J, p, c, lv, 1), M = life + lim, G = stopLine(M, 0, T);
  const G1 = stopLine(M, 10000, T);
  return {{nm, lv, life, lim, M, G, kiso: kisoKojo(G, T), G_j10000: G1}};
}});
console.log(JSON.stringify(out));
"""
res = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
ex = {r["nm"]: r for r in res}

doc = (ROOT / "scripts" / "teishi-setsumei.template.html").read_text(encoding="utf-8")
for nm, key in (("札幌市", "S"), ("長崎市", "N"), ("東京23区", "T")):
    r = ex[nm]
    for field, val in (("LIFE", r["life"]), ("LIM", r["lim"]), ("M", r["M"]), ("G", r["G"]), ("KISO", r["kiso"])):
        doc = doc.replace("{{%s_%s}}" % (key, field), yen(val))
    doc = doc.replace("{{%s_GMAN}}" % key, "%.1f" % (r["G"] / 10000))
doc = doc.replace("/*CALC*/", calc)
doc = doc.replace("/*EX*/", dump([[e[0], e[1], e[2], lv_of(e[1], e[2])] for e in EX]))
doc = doc.replace("/*KEIKA*/", dump(keika)).replace("/*KIJUN*/", dump(kijun)).replace("/*JUTAKU*/", dump(jutaku)).replace("/*KISO*/", dump(kiso))
left = re.findall(r"\{\{[A-Z_0-9]+\}\}", doc)
if left:
    sys.exit("差し込み忘れ: " + ",".join(sorted(set(left))))
(ROOT / "teishi-setsumei.html").write_text(add_snippet(doc), encoding="utf-8")

t = tool.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*KEIKA*/", dump(keika)).replace("/*KIJUN*/", dump(kijun)).replace("/*JUTAKU*/", dump(jutaku)).replace("/*KISO*/", dump(kiso))
(ROOT / "teishi.html").write_text(add_snippet(t), encoding="utf-8")
print("teishi-setsumei.html と teishi.html を生成しました")
for r in res: print(r)
