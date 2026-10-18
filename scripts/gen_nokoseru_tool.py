"""data/kiso_kojo.json の基礎控除額表と data/nokoseru.json の就労自立給付金の決まりを埋め込んで nokoseru.html（生活保護で働いたら、いくら残せる？）を生成する。

使い方: python3 scripts/gen_nokoseru_tool.py
生成後に python3 scripts/verify_nokoseru.py で、引用と計算を確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "nokoseru.json").read_text(encoding="utf-8"))
kiso = json.loads((ROOT / "data" / "kiso_kojo.json").read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

html = (ROOT / "scripts" / "nokoseru.template.html").read_text(encoding="utf-8")
for k, v in {
    "/*KISO*/": dump({"rows": kiso["rows"], "over": {k: kiso["over"][k] for k in ("from", "step", "add_first", "add_second")}}),
    "/*SHURO*/": dump({k: d["shuro"][k] for k in ("rate_pct", "add_tanshin", "add_fukusu", "max_tanshin", "max_fukusu", "months")}),
    "/*JIKAN_URL*/": d["sources"]["jikan"]["url"], "/*SHURO_URL*/": d["sources"]["shuro"]["url"],
    "/*CHECKED*/": d["checked"].replace("-", "年", 1).replace("-", "月", 1) + "日",
}.items():
    if k not in html:
        sys.exit(f"ひな形に {k} がない")
    html = html.replace(k, v)
(ROOT / "nokoseru.html").write_text(add_snippet(html), encoding="utf-8")
print("nokoseru.html を生成しました")
