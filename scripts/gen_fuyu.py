"""冬の上乗せの解説（fuyu-setsumei.html）とツール（fuyu.html）を、data/ から生成する。

使い方:
  python3 scripts/extract_fuyu.py   # 告示の表から data/fuyu.json を作る（表が変わったときだけ）
  python3 scripts/gen_fuyu.py
  python3 scripts/verify_fuyu.py    # 引用と金額を原本と照合する
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

fuyu = {k: v for k, v in load("fuyu.json").items() if k in ("touki", "period", "months", "pref_area", "kimatsu")}
kyuchi = load("kyuchi_by_city.json")["data"]
lv = lambda p, c: dict(kyuchi[p])[c]
# 解説の1章の例: [名前, 地区, 級地]
EX = [["札幌市", fuyu["pref_area"]["北海道"], lv("北海道", "札幌市")],
      ["長崎市", 6, lv("長崎県", "長崎市")],
      ["東京23区", 6, lv("東京都", "千代田区")]]

t = (ROOT / "scripts" / "fuyu-setsumei.template.html").read_text(encoding="utf-8")
t = t.replace("/*FUYU*/", dump(fuyu)).replace("/*EX*/", dump(EX))
(ROOT / "fuyu-setsumei.html").write_text(add_snippet(t), encoding="utf-8")

t = (ROOT / "scripts" / "fuyu.template.html").read_text(encoding="utf-8")
t = t.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*FUYU*/", dump(fuyu))
(ROOT / "fuyu.html").write_text(add_snippet(t), encoding="utf-8")
print("fuyu-setsumei.html と fuyu.html を生成しました（市区町村", sum(len(v) for v in kyuchi.values()), "件）")
