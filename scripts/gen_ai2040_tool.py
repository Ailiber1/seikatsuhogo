"""data/ai_shitsugyo.json の経済産業省「2040年の就業構造推計（改訂版）」の表を埋め込んで ai2040.html（2040年しごとしらべ）を生成する。

使い方: python3 scripts/gen_ai2040_tool.py
生成後に python3 scripts/verify_ai_shitsugyo.py で、表の数字が国の資料の写しと合っているか、判定が正しいかを確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "ai_shitsugyo.json").read_text(encoding="utf-8"))
m = d["meti"]
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

# 表の形が合っているか（列の数・都道府県が47そろっているか）
n = len(m["jobs"])
rows = [m["national"][k] for k in ("mismatch", "demand_2040", "supply_2040", "workers_2022")] + [x["mismatch"] for x in m["industries"]]
if any(len(r) != n for r in rows) or any(len(m["edu_by_job"][j]) != len(m["edus"]) for j in m["jobs"]):
    sys.exit("表の列の数が合わない")
prefs = [p for r in m["regions"] for p in r["prefs"]]
if len(prefs) != 47 or len(set(prefs)) != 47:
    sys.exit(f"都道府県が47そろっていない: {len(prefs)}")

tool = {k: m[k] for k in ("jobs", "national", "industries", "edu_total", "edu_by_job", "regions")}
html = (ROOT / "scripts" / "ai2040.template.html").read_text(encoding="utf-8")
html = html.replace("/*METI*/", dump(tool)).replace("/*METI_URL*/", d["sources"]["meti"]["url"]).replace("/*CHECKED*/", d["checked"].replace("-", "年", 1).replace("-", "月", 1) + "日")
(ROOT / "ai2040.html").write_text(add_snippet(html), encoding="utf-8")
print("ai2040.html を生成しました")
