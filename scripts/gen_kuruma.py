"""「車は持てる？」の解説（kuruma-setsumei.html）とツール（kuruma.html）を、data/kuruma.json から生成する。

使い方:
  python3 scripts/gen_kuruma.py
  python3 scripts/verify_kuruma.py   # 引用を原本と照合する
引用は data/kuruma.json から差し込む（原文のまま）。
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "kuruma.json").read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

NUM = "１２３４"
q = {
    "Q_PRINCIPLE": D["principle"]["q"],
    "Q_TSUKIN": "<br>".join(f"{NUM[i]}　{c['q']}" for i, c in enumerate(D["tsukin_cases"])),
    "Q_TSUKIN4": D["tsukin_extra"][3]["q"],
    "Q_TSUIN3": D["tsuin_cases"][1]["conds"][2]["q"],
    "Q_TSUIN4": D["tsuin_cases"][1]["conds"][3]["q"],
    "Q_KYU": D["kyushoku"]["q1"] + "（中略）" + D["kyushoku"]["q2"],
    "Q_KYU3": D["kyushoku"]["q3"],
    "Q_KAI": D["kaikae"]["q_rule"],
}
doc = (ROOT / "scripts" / "kuruma-setsumei.template.html").read_text(encoding="utf-8")
for k, v in q.items():
    assert "{{%s}}" % k in doc, k
    doc = doc.replace("{{%s}}" % k, v)
assert "{{" not in doc, "差し込み忘れ"
(ROOT / "kuruma-setsumei.html").write_text(add_snippet(doc), encoding="utf-8")

tool = (ROOT / "scripts" / "kuruma.template.html").read_text(encoding="utf-8").replace("/*DATA*/", dump(D))
(ROOT / "kuruma.html").write_text(add_snippet(tool), encoding="utf-8")
print("kuruma-setsumei.html と kuruma.html を生成しました")
