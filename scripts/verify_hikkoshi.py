"""引っ越し費用の資料・ツール（hikkoshi-setsumei.html / hikkoshi.html）の数字と引用を、原本と照合する。

1. data/hikkoshi.json の原文（18の場合・通知の引用）が、実施要領の原本PDFにそのままあるか
   （PDFは2段組みなので、ページを左右に切って読む）
2. ページに書いた原文の引用が、data/hikkoshi.json と同じか
3. ページに書いた金額の例が、data/tokubetsu_kijun.json・jutaku_limit.json から計算した額と同じか

使い方: python3 scripts/verify_hikkoshi.py
"""
import json, re, subprocess, html
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

d = json.loads((ROOT / "data" / "hikkoshi.json").read_text(encoding="utf-8"))
tk = json.loads((ROOT / "data" / "tokubetsu_kijun.json").read_text(encoding="utf-8"))
lim = json.loads((ROOT / "data" / "jutaku_limit.json").read_text(encoding="utf-8"))
ok = ng = 0
def check(cond, label):
    global ok, ng
    if cond: ok += 1
    else: ng += 1; print("不一致:", label)

# 1. 原文が原本にあるか
texts = [d["q30_lead"]] + [c["text"] for c in d["cases"]]
for q in d["quotes"].values():
    texts.append(q["text"])
    if "q" in q: texts.append(q["q"])
for t in texts:
    check(norm(t) in pdf_text, "原本にない: " + t[:40])
check(len(d["cases"]) == 18 and [c["no"] for c in d["cases"]] == list(range(1, 19)), "18の場合の番号")
check("1人2人3人4人5人6人1.31.41.51.61.71.7７人以上1.8" in pdf_text, "オの率の表（1人1.3〜7人以上1.8）")

# 2. ページの引用が元データと同じか（blockquote の中身）
def quotes_in(page):
    t = (ROOT / page).read_text(encoding="utf-8")
    return [norm(html.unescape(re.sub(r"<[^>]+>", "", m))) for m in re.findall(r"<blockquote>(.*?)</blockquote>", t, re.S)]
data_norm = {norm(t) for t in texts}
for page in ["hikkoshi-setsumei.html"]:
    if not (ROOT / page).exists(): continue
    for q in quotes_in(page):
        # 「（中略）」を入れた引用は、前後のかたまりがそれぞれ原文にあればよい
        pieces = [p for p in q.split("（中略）") if p]
        check(all(p in pdf_text for p in pieces), page + " の引用が原本にない: " + q[:40])

# 3. 金額の例
def shikikin(prefname, cityname, lv_index, n):
    row = tk["city"].get(cityname) or tk["pref"][prefname][str(lv_index // 2 + 1)]
    return row[min(n, 7) - 1] * 3
def limit(prefname, cityname, lv_index, n):
    row = lim["city"].get(cityname) or lim["pref"][prefname][str(lv_index // 2 + 1)]
    return row[0 if n == 1 else 1 if n == 2 else 2 if n <= 5 else 3 if n == 6 else 4]
EX = {  # ページに出す例: (都道府県, 市, 級地の番号0〜5, 人数) → (家賃の上限, 敷金等の上限)
    "長崎市・ひとり": (("長崎県", "長崎市", 2, 1), (36000, 141000)),
    "東京23区・ひとり": (("東京都", "千代田区", 0, 1), (53700, 209400)),
}
for k, (args, (lm, sk)) in EX.items():
    check(limit(*args) == lm, k + " 家賃の上限")
    check(shikikin(*args) == sk, k + " 敷金等の上限")
page = ROOT / "hikkoshi-setsumei.html"
if page.exists():
    t = page.read_text(encoding="utf-8")
    for k, (_, (lm, sk)) in EX.items():
        check(f"{sk:,}" in t, k + " の敷金等の上限がページにない")
print(f"照合: 一致 {ok} 件 / 不一致 {ng} 件")
if ng: raise SystemExit(1)
