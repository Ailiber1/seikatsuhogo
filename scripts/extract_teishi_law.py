"""e-Gov 法令検索から生活保護法の第8条（基準と程度の原則）・第26条（保護の停止及び廃止）を取得し、
data/teishi_law.json に書き出す（原文をそのまま。引用が条文にあるかを verify_teishi.py で確かめる）。

使い方: python3 scripts/extract_teishi_law.py
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

LAW_ID = "325AC0000000144"  # 生活保護法（昭和25年法律第144号）
URL = "https://laws.e-gov.go.jp/api/1/lawdata/" + LAW_ID
WANT = ["8", "26"]
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "teishi_law.json"

xml = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "seikatsuhogo-research"}), timeout=90).read()
root = ET.fromstring(xml)
if (root.findtext("./Result/Code") or "") != "0":
    sys.exit("e-Govから取得できない")
body = next(root.iter("MainProvision"), None)
if body is None:
    sys.exit("本則が見つからない")
out = {}
for a in body.iter("Article"):
    n = a.get("Num")
    if n in WANT and n not in out:
        paras = []
        for p in a.iter("Paragraph"):
            ps = p.find("ParagraphSentence")
            s = "".join(ps.itertext()).strip() if ps is not None else ""
            paras.append(" ".join(s.split()))
        out[n] = {"title": a.findtext("ArticleTitle") or "", "caption": (a.findtext("ArticleCaption") or "").strip("（）"), "paragraphs": paras}
missing = [n for n in WANT if n not in out]
if missing:
    sys.exit("条文が見つからない: " + ",".join(missing))
OUT.write_text(json.dumps({"source": URL, "law": "生活保護法", "articles": out}, ensure_ascii=False, indent=1), encoding="utf-8")
print("書き出しました:", OUT, {k: v["title"] + v["caption"] for k, v in out.items()})
