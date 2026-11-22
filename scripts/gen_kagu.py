"""ストーブ・布団・家具の解説（kagu-setsumei.html）とツール（kagu.html）を、data/kagu.json から生成する。

使い方:
  python3 scripts/gen_kagu.py
  python3 scripts/verify_kagu.py   # 原文と金額を実施要領の原本と照合する
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
kagu = json.loads((ROOT / "data" / "kagu.json").read_text(encoding="utf-8"))
kagu.pop("note", None)
dump = json.dumps(kagu, ensure_ascii=False, separators=(",", ":"))
for name in ("kagu-setsumei", "kagu"):
    t = (ROOT / "scripts" / f"{name}.template.html").read_text(encoding="utf-8").replace("/*KAGU*/", dump)
    (ROOT / f"{name}.html").write_text(add_snippet(t), encoding="utf-8")
print("kagu-setsumei.html と kagu.html を生成しました")
