"""data/ のためらう理由（原文つき）・級地・経過的加算・基準額・住宅扶助の上限を埋め込んで tamerai.html（ためらう理由チェック）を生成する。

使い方: python3 scripts/gen_tamerai_tool.py
生成後に python3 scripts/verify_tamerai.py で、生活扶助の計算がモデル世帯54件と一致するか・線より下かどうかの分け方が正しいかを確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
jutaku = {k: v for k, v in load("jutaku_limit.json").items() if k in ("pref", "city", "later_core_cities")}
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}
reasons = load("hosoku.json")["reasons"]

# 内部リンクの行き先が実在するか（打ちまちがいで切れたリンクを出さない）
for r in reasons:
    if not (ROOT / r["go"][1]).exists():
        sys.exit(f"リンク先がありません: {r['go'][1]}")

html = (ROOT / "scripts" / "tamerai.template.html").read_text(encoding="utf-8")
html = (html.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*KEIKA*/", dump(keika))
            .replace("/*KIJUN*/", dump(kijun)).replace("/*JUTAKU*/", dump(jutaku)).replace("/*REASONS*/", dump(reasons)))
(ROOT / "tamerai.html").write_text(add_snippet(html), encoding="utf-8")
print("tamerai.html を生成しました（理由", len(reasons), "件・市区町村", sum(len(v) for v in kyuchi.values()), "件）")
