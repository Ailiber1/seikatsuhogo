"""data/houritsu.json（場面ごとの答えと原文）を houritsu.template.html に埋め込んで houritsu.html（こんなとき、法律では？しらべ）を生成する。

使い方: python3 scripts/gen_houritsu_tool.py
生成後に python3 scripts/verify_houritsu.py で、引用が原文（法令・通知の写し）と一致するかを確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "houritsu.json").read_text(encoding="utf-8"))
# 内部リンクの行き先が実在するか（打ちまちがいで切れたリンクを出さない）
for s in data["situations"]:
    if s["go"] and not (ROOT / s["go"][1]).exists():
        sys.exit(f"リンク先がありません: {s['go'][1]}")
    if s["g"] not in {g["k"] for g in data["groups"]}:
        sys.exit(f"グループが不明: {s['k']}")
    for q in s["quotes"]:
        if q["s"] not in data["sources"]:
            sys.exit(f"出典が不明: {s['k']} {q['s']}")
pub = {k: data[k] for k in ("groups", "situations")}
pub["sources"] = {k: {"name": v["name"], "url": v["url"]} for k, v in data["sources"].items()}
html = (ROOT / "scripts" / "houritsu.template.html").read_text(encoding="utf-8")
html = html.replace("/*DATA*/", json.dumps(pub, ensure_ascii=False, separators=(",", ":")))
(ROOT / "houritsu.html").write_text(add_snippet(html), encoding="utf-8")
print("houritsu.html を生成しました（場面", len(data["situations"]), "件）")
