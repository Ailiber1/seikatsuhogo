"""data/kyuchi_by_city.json を埋め込んで tsuika.html（追加給付しらべ）を生成する。

使い方: python3 scripts/gen_tsuika_tool.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

kyuchi = json.loads((ROOT / "data" / "kyuchi_by_city.json").read_text(encoding="utf-8"))["data"]
template = (ROOT / "scripts" / "tsuika.template.html").read_text(encoding="utf-8")

html = template.replace("/*KYUCHI*/", json.dumps(kyuchi, ensure_ascii=False, separators=(",", ":")))
(ROOT / "tsuika.html").write_text(html, encoding="utf-8")
print("tsuika.html を生成しました（市区町村", sum(len(v) for v in kyuchi.values()), "件）")
