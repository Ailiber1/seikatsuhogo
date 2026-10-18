"""AIと失業の解説（ai-shitsugyo-setsumei.html）と2040年しごとしらべ（ai2040.html）の数字・引用を、元資料の写しと照合する。

- data/ai_shitsugyo.json の引用が、写し（PDF・HTML）の本文にそのまま入っているか（空白は無視して比べる）
- 件数・割合が写しに入っているか
- 経済産業省の表（職種・業界・学歴・地域）を写しのPDFから読み直し、data と1つ残らず一致するか
- 解説ページに書いた数字・引用が data と合っているか、ツールに埋め込んだ表が data と同じか

使い方: python3 scripts/verify_ai_shitsugyo.py   （pdftotext が必要）
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
d = json.loads((DATA / "ai_shitsugyo.json").read_text(encoding="utf-8"))
errors = []


def fail(msg):
    errors.append(msg)


def pdf_text(name, layout=True):
    args = ["pdftotext"] + (["-layout"] if layout else []) + [str(DATA / name), "-"]
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def html_text(path):
    t = path.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t).replace("&amp;", "&")


squash = lambda s: re.sub(r"\s+", "", s)
src = {k: squash(pdf_text(v["copy"]) if v["copy"].endswith(".pdf") else html_text(DATA / v["copy"])) for k, v in d["sources"].items()}

# 1. 引用が写しにそのまま入っているか
quotes = [("tdb", d["tdb"][k]) for k in ("quote_total", "quote_record", "quote_ai", "quote_why")]
quotes += [("tsr", d["tsr"][k]) for k in ("quote_yokusei", "quote_calm")]
quotes += [("challenger", d["challenger"]["quote"])]
quotes += [("stanford", d["stanford"][k]) for k in ("quote_gap", "quote_hiring", "quote_nowide")]
quotes += [("meti", d["meti"][k]) for k in ("quote_summary", "quote_premise")]
for k, q in quotes:
    if squash(q) not in src[k]:
        fail(f"引用が写しにない（{k}）: {q[:40]}…")

# 2. 件数・割合が写しに入っているか
t = d["tdb"]
must = {
    "tdb": [f"累計は{t['total_2026_1_5']}件", f"倒産は{t['tosan_2026_1_5']}件", f"休廃業・解散は{t['haigyo_2026_1_5']}件",
            f"前年（{t['tosan_2025']}件、1-5月：{t['tosan_2025_1_5']}）", f"（計{t['total_2025']}件）", f"前年同期（{t['haigyo_2025_1_5']}件）"],
    "tsr": [f"{d['tsr']['impact_pct']}％（{d['tsr']['impact_n']:,}社）", f"{d['tsr']['haichi_pct']}％", f"{d['tsr']['yokusei_pct']}％",
            f"{d['tsr']['none_pct']}％", f"有効回答{d['tsr']['answered']:,}社", f"{d['tsr']['kibo_taishoku_pct']}％"],
    "challenger": [f"{d['challenger']['ytd_cuts']:,}", f"{d['challenger']['ai_ytd']:,}", f"{d['challenger']['ai_sep']:,}", f"approximately{d['challenger']['ai_share_pct']}%"],
    "stanford": [f"{d['stanford']['young_gap_pct']}%below"],
    "rodo": [f"完全失業率（季節調整値）は{d['rodo']['rate_2026_08']}％", f"完全失業者数は{d['rodo']['unemployed_2026_08_man']}万人"],
}
for k, items in must.items():
    for s in items:
        if squash(s) not in src[k]:
            fail(f"写しに見つからない（{k}）: {s}")

# 3. 経済産業省の表を写しから読み直す
lines = pdf_text(d["sources"]["meti"]["copy"]).splitlines()
ints = lambda s: [int(x) for x in re.findall(r"-?[0-9]+", s)]


def find(start_pat, label, after=0, nth=0):
    """start_pat の行より後で、label を含む最初の行の、label より右の整数を返す（数字が無ければ次の行）"""
    s = next(i for i, l in enumerate(lines) if re.search(start_pat, l)) + after
    hits = [i for i in range(s, min(s + 40, len(lines))) if label in lines[i]]
    i = hits[nth]
    v = ints(lines[i].split(label, 1)[1])
    return v if v else ints(lines[i + 1])


m = d["meti"]
JOB = r"全国版就業構造推計（改訂版）・職種間ミスマッチ"
EDU = r"全国版就業構造推計（改訂版）・学歴間ミスマッチ"
pairs = lambda v: (v[0::2], v[1::2])
checks = {
    "職種・ミスマッチ": (find(JOB, "需給ミスマッチ"), m["national"]["mismatch"]),
    "職種・需要": (pairs(find(JOB, "需要数/供給数"))[0], m["national"]["demand_2040"]),
    "職種・供給": (pairs(find(JOB, "需要数/供給数"))[1], m["national"]["supply_2040"]),
    "職種・2022年": (find(JOB, "2022年就業者数"), m["national"]["workers_2022"]),
    "学歴・ミスマッチ": (find(EDU, "需給ミスマッチ"), m["edu_total"]["mismatch"]),
    "学歴・需要": (pairs(find(EDU, "需要数/供給数"))[0], m["edu_total"]["demand_2040"]),
    "学歴・供給": (pairs(find(EDU, "需要数/供給数"))[1], m["edu_total"]["supply_2040"]),
    "学歴・2022年": (find(EDU, "2022年就業者数"), m["edu_total"]["workers_2022"]),
}
for x in m["industries"]:
    checks["業界・" + x["name"]] = (find(JOB, x["name"]), x["mismatch"])
EDU_ROW = {"senmon": ("専門職", 0), "ai": ("の利活用を担う人材", 0), "jimu": ("事務職", 0), "genba": ("現場人材", 0), "seisan": ("うち生産工程従事者", 0), "sonota": ("うちその他現場人材", 0)}
for k, (label, nth) in EDU_ROW.items():
    checks["学歴×職種・" + k] = (find(EDU, label, after=10, nth=nth), m["edu_by_job"][k])
checks["地域"] = (find(r"地域別就業構造推計（地域別ミスマッチ×職種内訳）", "ミスマッチ数"), [r["mismatch"] for r in m["regions"]])
for name, (got, want) in checks.items():
    if got != want:
        fail(f"経産省の表と合わない（{name}）: 写し={got} data={want}")
for k, (dem, sup, mis) in enumerate(zip(m["national"]["demand_2040"], m["national"]["supply_2040"], m["national"]["mismatch"])):
    if sup - dem != mis:
        fail(f"供給−需要がミスマッチと合わない（{m['jobs'][k]}）: {sup}-{dem}≠{mis}")
reg_line = next(l for l in lines if "地域ブロック" in l and "近畿" in l)
order = ["近畿", "中部", "中国", "四国", "北海道", "東北", "九州"]
if [r["name"] for r in m["regions"][1:8]] != order or not re.search("近畿.*中部.*中国.*四国.*北海道.*東北.*九州", reg_line):
    fail("地域の並びが写しと合わない")
prefs = [p for r in m["regions"] for p in r["prefs"]]
if len(prefs) != 47 or len(set(prefs)) != 47:
    fail(f"都道府県が47そろっていない: {len(prefs)}")

# 4. 解説ページの数字・引用が data と合っているか
page = (ROOT / "ai-shitsugyo-setsumei.html").read_text(encoding="utf-8")
ptxt = squash(html_text(ROOT / "ai-shitsugyo-setsumei.html"))
for k, q in quotes:
    if q in (m["quote_premise"], t["quote_record"]):
        continue  # 前提は一部だけ「」で引用している。倒産だけの原文はやさしく言うとの中で数字だけ使う
    if squash(q).rstrip("。、") not in ptxt:
        fail(f"解説ページに引用がない: {q[:40]}…")
nat = dict(zip(m["jobs"], m["national"]["mismatch"]))
dem = dict(zip(m["jobs"], m["national"]["demand_2040"]))
sup = dict(zip(m["jobs"], m["national"]["supply_2040"]))
page_nums = [
    f"{t['tosan_2025']}件", f"{t['tosan_2026_1_5']}件", f"{t['tosan_2025_1_5']}件", f"{t['total_2026_1_5']}件",
    f"{d['tsr']['impact_pct']}%", f"{d['tsr']['yokusei_pct']}%", f"{d['tsr']['haichi_pct']}%", f"{d['tsr']['answered']:,}社",
    "12万136", f"約{d['challenger']['ai_share_pct']}%", "57万3,195人", f"{d['stanford']['young_gap_pct']}%少ない",
    f"約{nat['jimu']}万人が仕事に就けない", f"約{-nat['ai']}万人の人手不足", f"約{-nat['genba']}万人の人手不足",
    f"{sup['jimu']:,}万人いるのに", f"{dem['jimu']:,}万人", f"{d['rodo']['rate_2026_08']}%",
    f"{t['tosan_2025_1_5'] + t['haigyo_2025_1_5']}件は、倒産{t['tosan_2025_1_5']}件＋休廃業・解散{t['haigyo_2025_1_5']}件の計算",
    f"毎週およそ{round(t['total_2026_1_5'] / (151 / 7))}社", f"{t['total_2026_1_5']}件÷約{151 / 7:.1f}週",
    f"去年より{t['total_2026_1_5'] - t['tosan_2025_1_5'] - t['haigyo_2025_1_5']}件", "600件超", f"{t['total_2026_1_5']}社",
]
if t["tosan_2026_1_5"] + t["haigyo_2026_1_5"] != t["total_2026_1_5"]:
    fail("2026年1〜5月の倒産＋休廃業が242件にならない")
for s in page_nums:
    if squash(s) not in ptxt:
        fail(f"解説ページに数字がない（または違う）: {s}")
if d["challenger"]["ai_ytd"] != 120136:
    fail("12万136 の表記が data と合わない")
for w, want in [("77.6", -nat["ai"] / nat["jimu"] * 100), ("59.5", -nat["genba"] / nat["jimu"] * 100),
                ("90.1", (t["tosan_2025_1_5"] + t["haigyo_2025_1_5"]) / t["total_2026_1_5"] * 100)]:
    if abs(float(w) - want) > 0.05 or f'data-w="{w}"' not in page:
        fail(f"棒の長さが合わない: {w} / {want:.1f}")

# 5. ツールに埋め込んだ表が data と同じか
tool = (ROOT / "ai2040.html").read_text(encoding="utf-8")
emb = json.loads(re.search(r"const M = (\{.*?\});\n", tool).group(1))
for k in ("jobs", "national", "industries", "edu_total", "edu_by_job", "regions"):
    if emb[k] != m[k]:
        fail(f"ツールの表が data と違う: {k}（gen_ai2040_tool.py を実行し直す）")
if "gcUse('2040しごとしらべ')" not in tool:
    fail("ツールに利用回数の計測がない")

if errors:
    print("合わないところがあります:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: 引用{len(quotes)}件・件数{sum(map(len, must.values()))}件・経産省の表{len(checks)}行・解説の数字{len(page_nums)}件・ツールの表が、写しと data と一致しました")
