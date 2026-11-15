"""車の解説（kuruma-setsumei.html）とツール（kuruma.html）を、原本と照合する。

1. data/kuruma.json の引用が、実施要領の原本PDF（2段組みを左右に分けて読む）・厚労省ページの写しにそのままあるか
2. 解説の引用（blockquote）が、同じ原本にそのままあるか（「（中略）」の前後は別々に確かめる）
3. 条件の数：通勤は4つの場合・2〜4に付く条件は4つ、通院は2つの場合×5つの条件、買い替えは4つ。原本の番号と合っているか
4. ツールに埋め込んだデータが data/kuruma.json と同じか、計測・作成者表記・リンク先があるか

使い方: python3 scripts/verify_kuruma.py
"""
import json, re, html, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
norm = lambda s: re.sub(r"\s+", "", s)
ok = ng = 0
def check(c, label):
    global ok, ng
    if c: ok += 1
    else: ng += 1; print("不一致:", label)

def pdf_cols(path):
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
    w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    out = []
    for p in range(1, pages + 1):
        for x in (0, w / 2):
            out.append(subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-x", str(int(x)), "-y", "0", "-W", str(int(w / 2)), "-H", str(int(h)), str(path), "-"],
                                      capture_output=True, text=True).stdout)
    return out

D = json.loads((DATA / "kuruma.json").read_text(encoding="utf-8"))
cols = pdf_cols(DATA / "jisshi_yoryo_r8_source.pdf")
pdf_text = norm("".join(cols))
page_text = norm(html.unescape(re.sub(r"<[^>]+>", " ", (DATA / "seikatsuhogo_page_source.html").read_text(encoding="utf-8"))))
in_src = lambda s: s in pdf_text or s in page_text

# 1. データの引用
qs = [D["principle"]["q"], D["tsukin_rule"]["q"], D["tsukin_extra_intro"]["q"], D["kyushoku"]["q1"], D["kyushoku"]["q2"], D["kyushoku"]["q3"], D["kaikae"]["q_rule"]]
qs += [c["q"] for c in D["tsukin_cases"]] + [c["q"] for c in D["tsukin_extra"]]
qs += [x["q"] for c in D["tsuin_cases"] for x in c["conds"]] + [c["q"] for c in D["kyushoku"]["conds"]] + [c["q"] for c in D["kaikae"]["conds"]]
for s in qs:
    check(in_src(norm(s)), "データの引用が原本にない: " + s[:40])

# 2. 解説・ツールの引用
for name in ("kuruma-setsumei.html", "kuruma.html"):
    t = (ROOT / name).read_text(encoding="utf-8")
    for b in re.findall(r"<blockquote[^>]*>(.*?)</blockquote>", t, re.S):
        b = norm(html.unescape(re.sub(r"<[^>]+>", "", b)))
        if "{{" in b or "esc(" in b: continue
        pieces = [p for p in b.split("（中略）") if p]
        check(all(in_src(p) for p in pieces), name + " の引用が原本にない: " + b[:40])

# 3. 条件の数と、原本の番号
check(len(D["tsukin_cases"]) == 4 and all(norm(c["q"]) in pdf_text for c in D["tsukin_cases"]), "通勤は4つの場合")
for i, c in enumerate(D["tsukin_cases"]):
    check(norm("１２３４"[i] + c["q"]) in pdf_text, f"通勤の場合{i + 1}の番号と文")
check(len(D["tsukin_extra"]) == 4, "通勤の追加条件は4つ")
for i, c in enumerate(D["tsukin_extra"]):
    check(norm(f"({i + 1}){c['q']}") in pdf_text, f"通勤の追加条件({i + 1})の番号と文")
check(len(D["tsuin_cases"]) == 2 and all(len(c["conds"]) == 5 for c in D["tsuin_cases"]), "通院は2つの場合×5つの条件")
for c in D["tsuin_cases"]:
    for i, x in enumerate(c["conds"]):
        check(norm(f"({i + 1}){x['q']}") in pdf_text, f"通院の条件({i + 1})の番号と文: " + x["q"][:20])
check(len(D["kaikae"]["conds"]) == 4, "買い替えは4つ")
for i, c in enumerate(D["kaikae"]["conds"]):
    check(norm("１２３４"[i] + c["q"]) in pdf_text, f"買い替えの条件{i + 1}の番号と文")
# 通院の「5つ」は、(6)が無いこと（5つで終わること）も確かめる
check("(6)自動車の維持" not in pdf_text and "(6)当該者自身が運転" not in pdf_text, "通院の条件に(6)が無い")
# 排気量2,000cc・事前の承認
check(norm("排気量がおおむね2,000㏄以下") in pdf_text, "排気量2,000cc")

# 4. ツール・解説の体裁
tool = (ROOT / "kuruma.html").read_text(encoding="utf-8")
doc = (ROOT / "kuruma-setsumei.html").read_text(encoding="utf-8")
m = re.search(r"const D = (\{.*?\});\nconst \$ =", tool, re.S)
check(m is not None and json.loads(m.group(1)) == D, "ツールの埋め込みデータが data/kuruma.json と同じ")
check("data-goatcounter" in tool and "data-goatcounter" in doc, "計測が入っている")
check("gcUse('車は持てる？しらべ')" in tool, "利用回数の呼び出し")
check("作成：" in tool and "作成：" in doc, "作成者表記")
check("どこにも送信していません。ページが開かれた回数と結果が出た回数だけは、Cookieを使わず、個人を特定しない方法で数えています。" in tool, "ツールの注意書き")
for page, t in (("tool", tool), ("doc", doc)):
    for href in set(re.findall(r'href="([a-z0-9\-]+\.html)"', t)):
        check((ROOT / href).exists(), f"{page} の内部リンク先がある: {href}")
# 解説の数字（4つ・5つ・2,000cc・6か月）が、データの数と同じか
check("通勤：認められるのは4つの場合" in doc and "条件は5つ" in doc and "買い替えの条件は4つ" in doc, "解説の見出しの数")

print(f"\n一致 {ok} 件 / 不一致 {ng} 件")
raise SystemExit(1 if ng else 0)
