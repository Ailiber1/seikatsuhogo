"""e-Gov 法令検索から生活保護法を取得し、「窓口では教えてくれない法律5つ」の資料で引用する条文を
data/houritsu_law.json に書き出す（原文をそのまま。引用が条文にあるかを verify_houritsu.py で確かめる）。

使い方: python3 scripts/extract_yatte_law.py
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

LAW_ID = "325AC0000000144"  # 生活保護法（昭和25年法律第144号）
URL = "https://laws.e-gov.go.jp/api/1/lawdata/" + LAW_ID
WANT = ["2", "7", "24", "27", "56", "57", "58", "62", "64", "65", "69"]
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "houritsu_law.json"

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
    "checked": "2026-11-02", "articles": out,
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("書き出しました:", OUT, "条:", ",".join(WANT))


# 行政不服審査法（平成26年法律第68号）: 審査請求の期間（18条）と、処分のときの教示（82条）
GY_ID = "426AC0000000068"
GY_URL = "https://laws.e-gov.go.jp/api/1/lawdata/" + GY_ID
gy_xml = urllib.request.urlopen(urllib.request.Request(GY_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=90).read()
gy_root = ET.fromstring(gy_xml)
gy = {}
for a in gy_root.iter("Article"):
    n = a.get("Num")
    if n in ("18", "82") and n not in gy:
        paras = []
        for p in a.iter("Paragraph"):
            ps = p.find("ParagraphSentence")
            s = "".join(ps.itertext()).strip() if ps is not None else ""
            paras.append(" ".join(s.split()))
        gy[n] = {"title": a.findtext("ArticleTitle") or "", "caption": (a.findtext("ArticleCaption") or "").strip("（）"), "paragraphs": paras}
if set(gy) != {"18", "82"}:
    sys.exit("行政不服審査法の条文が見つからない: %s" % sorted(gy))
data = json.loads(OUT.read_text(encoding="utf-8"))
data["gyoshin"] = {"source": {"title": "行政不服審査法（平成26年法律第68号）", "url": "https://laws.e-gov.go.jp/law/" + GY_ID, "api": GY_URL}, "articles": gy}
OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("行政不服審査法 18条・82条も書き出しました")
