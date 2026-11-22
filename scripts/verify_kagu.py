"""ストーブ・布団・家具の資料とツール（kagu-setsumei.html / kagu.html）の原文と金額を、原本と照合する。

1. data/kagu.json の原文（5つの場面・通知の引用）が、実施要領の原本PDFにそのままあるか
   （PDFは2段組みなので、ページを左右に切って読む。「（中略）」を入れた引用は前後のかたまりごとに確かめる）
2. 金額が原本にあるか
3. ページに書いた引用（blockquote）が原本にあるか

使い方: python3 scripts/verify_kagu.py
"""
import json, re, subprocess, html, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "data" / "jisshi_yoryo_r8_source.pdf"
norm = lambda s: re.sub(r"\s+", "", s)

info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
parts = []
for p in range(1, pages + 1):
    for x in (0, w / 2):
        parts.append(subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-x", str(int(x)), "-y", "0",
                                     "-W", str(int(w / 2)), "-H", str(int(h)), str(PDF), "-"],
                                    capture_output=True, text=True).stdout)
pdf_text = norm("".join(parts))

d = json.loads((ROOT / "data" / "kagu.json").read_text(encoding="utf-8"))
ok = ng = 0
def check(cond, label):
    global ok, ng
    if cond: ok += 1
    else: ng += 1; print("不一致:", label)
def in_pdf(t):
    return all(norm(p) in pdf_text for p in t.split("（中略）") if p.strip())

# 1. 原文
for c in d["cases"]:
    check(in_pdf(c["text"]), "場面 " + c["key"])
for k, q in d["quotes"].items():
    check(in_pdf(q["text"]), "引用 " + k)

# 2. 金額
a = d["amounts"]
check("36,700円の範囲内" in pdf_text and "58,400円の範" in pdf_text, "家具 36,700円・58,400円")
check("31,000円の範囲内" in pdf_text and "78,000円の範囲内" in pdf_text, "暖房 31,000円・78,000円")
check("１組につき15,300円以内" in pdf_text and "１組につき22,500円以内" in pdf_text, "布団 15,300円・22,500円")
check("２人まで22,500円以内40,300円以内４人まで42,800円以内68,200円以内５人55,000円以内86,800円以内６人以上１人を8,000円以内11,900円以内" in pdf_text, "災害の世帯人員別の表")
check((a["kagu"], a["kagu_max"], a["danbo"], a["danbo_ff"], a["reibo"], a["futon_saisei"], a["futon_shinki"]) == (36700, 58400, 31000, 78000, 78000, 15300, 22500), "json の金額")

# 3. ページの引用
for page in ["kagu-setsumei.html", "kagu.html"]:
    f = ROOT / page
    if not f.exists(): continue
    t = f.read_text(encoding="utf-8")
    for m in re.findall(r"<blockquote>(.*?)</blockquote>", t, re.S):
        q = html.unescape(re.sub(r"<[^>]+>", "", m))
        if "${" in q:  # ツールの中で data/kagu.json から差し込む部分（中身は1.で照合済み）
            continue
        check(in_pdf(q), page + " の引用: " + q[:30])

print(f"一致 {ok} 件 / 不一致 {ng} 件")
sys.exit(1 if ng else 0)
