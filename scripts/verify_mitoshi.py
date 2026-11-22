"""mitoshi-setsumei.html / mitoshi.html の引用・数字を原本と照合し、計算を確かめる。

原本: data/kijunbukai64_shiryo1_source.pdf（第64回 生活保護基準部会 資料1、2026-11-17）
必要: pdftotext（poppler）
使い方: python3 scripts/verify_mitoshi.py
"""
import json, math, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = subprocess.run(["pdftotext", "-layout", str(ROOT / "data" / "kijunbukai64_shiryo1_source.pdf"), "-"],
                     capture_output=True, text=True, check=True).stdout
norm = lambda s: re.sub(r"\s+", "", s)
S = norm(src)
doc = (ROOT / "mitoshi-setsumei.html").read_text(encoding="utf-8")
ok = ng = 0

def check(label, cond):
    global ok, ng
    if cond: ok += 1
    else:
        ng += 1; print("NG:", label)

# 1. 解説の引用（blockquote）が原本にそのまま有るか（第64回資料1の範囲のもの）
for q in re.findall(r"<blockquote>(.*?)</blockquote>", doc, re.S):
    check("引用: " + q[:30], norm(q) in S)

# 2. data/mitoshi.json の数字が原本に有るか
m = json.loads((ROOT / "data" / "mitoshi.json").read_text(encoding="utf-8"))
f = m["fufuko"]
for k in ("kijun_r6", "kijun_r8", "shishutsu_r6", "sa_r6", "sa_r8", "shishutsu_r1", "kijun_r4kensho"):
    check(f"数字 {k}={f[k]:,}", f"{f[k]:,}" in S)
check("標準誤差 5285", "［5285］" in S)
check("243世帯・4世帯", "（243世帯）" in S and "（４世帯）" in S)
check("12.3％・9.0％", "17,709円（12.3％）" in S and "13,317円（9.0％）" in S)
check("前回 1.020", "1.020" in S)
check("食料 50,370→67,485", "食料50,370円67,485円12.2%" in S)
check("物価+12.0%・賃金+10.4%", "R元年→R７年：+12.0%" in S and "R元年→R７年：+10.4%" in S)
check("差の計算", f["shishutsu_r6"] - f["kijun_r8"] == f["sa_r8"] and f["shishutsu_r6"] - f["kijun_r6"] == f["sa_r6"])

# 3. 世帯構成別の表（年収階級の行）: 今回・展開後・前回・前回展開後 の並び
rows = {
    "fufuko":  "夫婦子１人世帯年収階級72%70%37.7%71%71%",
    "k_fu65":  "年収階級63%64%47.3%64%60%",
    "k_tan65": "年収階級63%64%71.6%63%62%",
    "k_fu75":  "年収階級68%64%51.6%65%58%",
    "k_tan75": "年収階級56%58%39.3%65%55%",
    "tanshin": "単身世帯（65歳未満勤労者）年収階級82%67%62.1%71%65%",
}
for r in m["setai_kosei"]:
    pat = rows[r["key"]]
    check("表の行（原本）" + r["key"], pat in S)
    nums = re.findall(r"(\d+)%", pat)
    check("表の行（json）" + r["key"], [int(nums[0]), int(nums[1]), int(nums[3]), int(nums[4])] == [r["now"], r["ten"], r["prev"], r["prev_ten"]])

# 4. 計算（hogohi と同じ式）: モデル世帯の期待値と、解説7章の長崎市の額
K = json.loads((ROOT / "data" / "kijun_r8.json").read_text(encoding="utf-8"))
KE = json.loads((ROOT / "data" / "keika.json").read_text(encoding="utf-8"))["data"]
def calc(ages, lv):
    n = len(ages); raw = sum(K["dai1"][a][lv] for a in ages)
    d1 = math.ceil(math.floor(round(raw * K["teigen"][str(n)] * 1e6) / 1e6) / 10) * 10
    kei = sum(KE[str(n)][a][lv] - min(1000, KE[str(n)][a][lv]) for a in ages)
    return d1, K["dai2"][str(n)], K["tokurei"]["from_2026_10"] * n, kei
for mh in K["model_households"]:
    for lv, (_, oct_) in mh["expect"].items():
        check("モデル世帯 " + mh["name"] + " " + lv, sum(calc(mh["ages"], int(lv))) == oct_)
d1, d2, tok, kei = calc(["20～40"], 2)  # 長崎市 = 2級地-1
check("長崎市ひとり 73,930円", (d1, d2, tok, kei) == (43640, 27790, 2500, 0) and "73,930円" in doc and "43,640円" in doc)
check("1%で約740円", round(73930 * 0.01 / 10) * 10 == 740 and "約740円" in doc)
check("9.0%で約6,650円", round(73930 * 0.09 / 10) * 10 == 6650 and "約6,650円" in doc)
check("棒の幅", "91.8" in doc and round(f["kijun_r8"] / f["shishutsu_r6"] * 100, 1) == 91.8 and round(f["kijun_r6"] / f["shishutsu_r6"] * 100, 1) == 89.1)

print(f"一致 {ok} 件 / 不一致 {ng} 件")
sys.exit(1 if ng else 0)
