"""data/kiso_kojo.json（基礎控除額表）を埋め込んで kyuryo.html（給料いくら残るしらべ）を生成する。

使い方: python3 scripts/gen_kyuryo_tool.py
生成後に python3 scripts/verify_kyuryo.py で、基礎控除額表の全区分と一致するか確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
kiso = json.loads((ROOT / "data" / "kiso_kojo.json").read_text(encoding="utf-8"))
kiso = {k: kiso[k] for k in ("rows", "over", "other")}
html = (ROOT / "scripts" / "kyuryo.template.html").read_text(encoding="utf-8")
html = html.replace("/*KISO*/", json.dumps(kiso, ensure_ascii=False, separators=(",", ":")))
(ROOT / "kyuryo.html").write_text(add_snippet(html), encoding="utf-8")
print("kyuryo.html を生成しました（基礎控除額表", len(kiso["rows"]), "区分）")
