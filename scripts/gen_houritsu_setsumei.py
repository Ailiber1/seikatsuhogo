"""hosoku-setsumei.html の見た目（CSS）を土台に、houritsu-setsumei.body.html の本文をつないで houritsu-setsumei.html（資料）を生成する。

使い方: python3 scripts/gen_houritsu_setsumei.py
引用は verify_houritsu.py が原文（法令・通知の写し）と突き合わせる。
"""
import re
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet

ROOT = Path(__file__).resolve().parent.parent
base = (ROOT / "scripts" / "houritsu-base-head.html").read_text(encoding="utf-8")
body = (ROOT / "scripts" / "houritsu-setsumei.body.html").read_text(encoding="utf-8")
for href in set(re.findall(r'href="([a-z0-9-]+\.html)"', body)):
    if not (ROOT / href).exists():
        sys.exit(f"リンク先がありません: {href}")
(ROOT / "houritsu-setsumei.html").write_text(add_snippet(base + body), encoding="utf-8")
print("houritsu-setsumei.html を生成しました")
