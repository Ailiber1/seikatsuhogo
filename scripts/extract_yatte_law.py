"""e-Gov 法令検索から生活保護法を取得し、「やってはいけないこと」の資料で引用する条文を
data/yatte_law.json に書き出す（原文をそのまま。引用が条文にあるかを verify_yatte.py で確かめる）。

使い方: python3 scripts/extract_yatte_law.py
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

LAW_ID = "325AC0000000144"  # 生活保護法（昭和25年法律第144号）
URL = "https://laws.e-gov.go.jp/api/1/lawdata/" + LAW_ID
WANT = ["4", "27", "28", "29", "60", "61", "62", "63", "78", "85"]
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "yatte_law.json"

xml = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=90).read()
root = ET.fromstring(xml)
if (root.findtext("./Result/Code") or "") != "0":
    sys.exit("e-Govから取得できない")
body = None
for e in root.iter("MainProvision"):
    body = e
    break
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
    sys.exit("条文が見つからない: %s" % missing)
OUT.write_text(json.dumps({
    "source": {"title": "生活保護法（昭和25年法律第144号）", "url": "https://laws.e-gov.go.jp/law/" + LAW_ID, "api": URL},
    "checked": "2026-10-25", "articles": out,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("書き出しました:", OUT, "条:", ",".join(WANT))
