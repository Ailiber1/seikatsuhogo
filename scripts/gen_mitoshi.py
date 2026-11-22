"""見直しの解説（mitoshi-setsumei.html）とツール（mitoshi.html）を、data/ から生成する。

使い方:
  python3 scripts/gen_mitoshi.py
  python3 scripts/verify_mitoshi.py   # 引用と数字を原本（第64回 基準部会 資料1）と照合し、計算を確かめる
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

m = {k: v for k, v in load("mitoshi.json").items() if k in ("fufuko", "setai_kosei")}
kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}

t = (ROOT / "scripts" / "mitoshi-setsumei.template.html").read_text(encoding="utf-8")
t = t.replace("/*MITOSHI*/", dump(m))
(ROOT / "mitoshi-setsumei.html").write_text(add_snippet(t), encoding="utf-8")

t = (ROOT / "scripts" / "mitoshi.template.html").read_text(encoding="utf-8")
t = t.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*KEIKA*/", dump(keika)).replace("/*KIJUN*/", dump(kijun)).replace("/*MITOSHI*/", dump(m))
(ROOT / "mitoshi.html").write_text(add_snippet(t), encoding="utf-8")
print("mitoshi-setsumei.html と mitoshi.html を生成しました（市区町村", sum(len(v) for v in kyuchi.values()), "件）")
