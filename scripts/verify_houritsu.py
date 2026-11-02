"""資料（houritsu-setsumei.html）とツール（houritsu.html）の引用が、原文（法令の取得結果・通知の写し）にそのまま入っているかを確かめる。

- 引用の「（中略）」の前後は、別々に原文にあるか確かめる
- 空白と改行は無視して比べる
- ツールに埋め込んだデータが data/houritsu.json と同じか、内部リンクの行き先があるかも確かめる

使い方: python3 scripts/verify_houritsu.py   （問題があれば終了コード1）
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ws = lambda s: re.sub(r"\s+", "", s)
errors = []

def text_of_html(path):
    t = (ROOT / "data" / path).read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return ws(html.unescape(re.sub(r"<[^>]+>", "", t)))

law = json.loads((ROOT / "data" / "houritsu_law.json").read_text(encoding="utf-8"))
def law_text(d):
    return ws("".join(p for a in d["articles"].values() for p in a["paragraphs"]))

data = json.loads((ROOT / "data" / "houritsu.json").read_text(encoding="utf-8"))
corpus = {
    "law": law_text(law),
    "gyoshin": law_text(law["gyoshin"]),
    "jikan": text_of_html("jikan_tsuchi_dai9_source.html"),
    "kacho": text_of_html("kacho_tsuchi_dai9_source.html"),
    "mhlw": text_of_html("seikatsuhogo_page_source.html"),
}

def check(quote, srcs, where):
    for part in quote.split("（中略）"):
        p = ws(part)
        if p and not any(p in corpus[s] for s in srcs):
            errors.append(f"原文にありません [{where}]: {part[:50]}…")

n = 0
for s in data["situations"]:
    for q in s["quotes"]:
        check(q["t"], [q["s"]], f"ツール {s['k']} {q['c']}"); n += 1
print(f"ツールの引用 {n}件を確認")

# 資料の引用（blockquote）は、どれかの原文に入っていること
doc = (ROOT / "houritsu-setsumei.html").read_text(encoding="utf-8")
bq = re.findall(r"<blockquote>(.*?)</blockquote>", doc, flags=re.S)
for b in bq:
    check(html.unescape(re.sub(r"<[^>]+>", "", b)), list(corpus), "資料")
print(f"資料の引用 {len(bq)}件を確認")

# ツールに埋め込んだデータが json と同じか
tool = (ROOT / "houritsu.html").read_text(encoding="utf-8")
m = re.search(r"const DATA = (\{.*?\});\nconst \$", tool, flags=re.S)
if not m:
    errors.append("ツールに埋め込んだデータが見つかりません")
else:
    emb = json.loads(m.group(1))
    if emb["situations"] != data["situations"] or emb["groups"] != data["groups"]:
        errors.append("ツールの埋め込みデータが data/houritsu.json と違います（gen_houritsu_tool.py を実行し直す）")

# 内部リンク
for name in ("houritsu-setsumei.html", "houritsu.html"):
    for href in set(re.findall(r'href="([a-z0-9-]+\.html)"', (ROOT / name).read_text(encoding="utf-8"))):
        if not (ROOT / href).exists():
            errors.append(f"{name}: リンク先がありません {href}")
for need in ("計測", ):
    pass
for name in ("houritsu-setsumei.html", "houritsu.html"):
    if "data-goatcounter" not in (ROOT / name).read_text(encoding="utf-8"):
        errors.append(f"{name}: 計測が入っていません")
if "gcUse(" not in tool:
    errors.append("ツール: gcUse がありません")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("OK: 引用はすべて原文と一致、リンク・計測・埋め込みも問題なし")
