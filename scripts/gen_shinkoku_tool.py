"""data/shinkoku.json の収入の種類と次官通知の原文を埋め込んで shinkoku.html（これは申告がいる？収入チェック）を生成する。

使い方: python3 scripts/gen_shinkoku_tool.py
生成後に python3 scripts/verify_yatte.py で、引用が原本の写しに入っているかと、計算を確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "shinkoku.json").read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

html = (ROOT / "scripts" / "shinkoku.template.html").read_text(encoding="utf-8")
for k, v in {
    "/*DATA*/": dump({"items": d["items"], "sources": d["sources"], "common_quote": d["common_quote"]}),
    "/*JIKAN_URL*/": d["sources"]["jikan"]["url"], "/*LAW_URL*/": d["sources"]["law"]["url"],
    "/*CHECKED*/": d["checked"].replace("-", "年", 1).replace("-", "月", 1) + "日",
}.items():
    if k not in html:
        sys.exit(f"ひな形に {k} がない")
    html = html.replace(k, v)
(ROOT / "shinkoku.html").write_text(add_snippet(html), encoding="utf-8")
print("shinkoku.html を生成しました")
