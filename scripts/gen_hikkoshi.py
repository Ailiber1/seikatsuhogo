"""引っ越し費用の解説（hikkoshi-setsumei.html）とツール（hikkoshi.html）を、data/ から生成する。

使い方:
  python3 scripts/extract_tokubetsu_kijun.py   # 特別基準額の表（data/tokubetsu_kijun.json）を作る。表が変わったときだけ
  python3 scripts/gen_hikkoshi.py
  python3 scripts/verify_hikkoshi.py           # 原文と金額を原本と照合する
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

hk = load("hikkoshi.json")
cases = [{k: c[k] for k in ("no", "group", "plain", "text")} for c in hk["cases"]]
groups = hk["groups"]

# 解説
t = (ROOT / "scripts" / "hikkoshi-setsumei.template.html").read_text(encoding="utf-8")
t = t.replace("/*CASES*/", dump(cases)).replace("/*GROUPS*/", dump(groups))
(ROOT / "hikkoshi-setsumei.html").write_text(add_snippet(t), encoding="utf-8")

# ツール
kyuchi = load("kyuchi_by_city.json")["data"]
jutaku = {k: v for k, v in load("jutaku_limit.json").items() if k in ("pref", "city", "later_core_cities")}
toku = {k: v for k, v in load("tokubetsu_kijun.json").items() if k in ("pref", "city")}
d = {"q30_lead": hk["q30_lead"], "cases": cases, "groups": groups}
t = (ROOT / "scripts" / "hikkoshi.template.html").read_text(encoding="utf-8")
t = (t.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*JUTAKU*/", dump(jutaku))
      .replace("/*TOKU*/", dump(toku)).replace("/*HIKKOSHI*/", dump(d)))
(ROOT / "hikkoshi.html").write_text(add_snippet(t), encoding="utf-8")
print("hikkoshi-setsumei.html と hikkoshi.html を生成しました（18の場合", len(cases), "件・市区町村", sum(len(v) for v in kyuchi.values()), "件）")
