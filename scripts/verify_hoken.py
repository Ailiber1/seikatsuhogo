"""失業保険の解説（hoken-setsumei.html）と、何か月もつ？しらべ（motsu.html）の数字・引用を、元資料の写しと照合する。

- data/shitsugyo_hoken.json の引用が、写し（PDF・HTML）の本文にそのまま入っているか（空白は無視して比べる）
- 件数・割合が写しに入っているか、計算した数字（175万人・24.4%・約132万人など）が合っているか
- 解説ページに書いた数字・引用が data と合っているか、ツールに埋め込んだ数字が data と同じか
- ツールの試算（貯金が何か月目に尽きるか）を、ここで同じ決まりで計算し直した値の表として出す（Playwright で突き合わせる）

使い方: python3 scripts/verify_hoken.py   （pdftotext が必要）
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
d = json.loads((DATA / "shitsugyo_hoken.json").read_text(encoding="utf-8"))
errors = []
fail = errors.append
import unicodedata
# 全角・半角の数字やかっこの違いは無視して比べる（原文は「６万人」、こちらは「6万人」など）
squash = lambda s: re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def text(name):
    p = DATA / name
    if name.endswith(".pdf"):
        return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, check=True).stdout
    t = p.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


src = {k: squash(text(v["copy"])) for k, v in d["sources"].items()}

# 1. 引用が写しにそのまま入っているか
quotes = [("nenpo", d["nenpo"]["quote"]), ("nenpo", d["nenpo"]["quote_kounen"]),
          ("nendo", d["nendo"]["quote_total"]), ("nendo", d["nendo"]["quote_arata"]),
          ("shosai", d["shosai"]["quote"]),
          ("kaisei", d["kaisei"]["quote_kakudai"]), ("kaisei", d["kaisei"]["quote_seigen"]), ("kaisei", d["kaisei"]["sekou"]),
          ("hw", d["hw"]["quote_jouken"]), ("hw", d["hw"]["quote_byouki"]), ("hw_proc", d["hw"]["quote_taiki"])]
for k, q in quotes:
    if squash(q) not in src[k]:
        fail(f"引用が写しにない（{k}）: {q[:40]}…")

# 2. 件数・割合が写しに入っているか
n, s = d["nendo"], d["shosai"]
must = {
    "nendo": [f"仕事をやめたため求職・・・・・・・・・・・・{n['yameta_man']}万人", f"非自発的な離職・・・・・・・・・・・・{n['hijihatsu_man']}万人",
              f"自発的な離職(自己都合)・・・・・・・・・{n['jihatsu_man']}万人", f"学卒未就職・・・・・・・・・・・・・{n['gakusotsu_man']}万人",
              f"収入を得る必要が生じたから・・・・・・・{n['shunyu_man']}万人", f"その他・・・・・・・・・・・・・・・{n['sonota_man']}万人"],
    "shosai": [f"失業者数は{s['shitsugyosha_man']}万人", f"「３か月未満」が{s['m3_man']}万人", f"「３か月以上」が{s['over3_man']}万人"]
             + [f"{v}" for v in s["pct"].values()],
    "kaisei": [f"約{d['kaisei']['man_10_19h']}万人"],
    "days": [f"{d['days']['min']}日", f"{d['days']['max']}日"],
}
for k, items in must.items():
    for x in items:
        if squash(x) not in src[k]:
            fail(f"写しに見つからない（{k}）: {x}")
if n["shitsugyo_2025_man"] - n["zou_man"] != n["shitsugyo_2024_man"]:
    fail("2024年度の失業者数（180−5）が合わない")
if n["yameta_man"] != n["hijihatsu_man"] + n["jihatsu_man"] or n["arata_man"] != n["gakusotsu_man"] + n["shunyu_man"] + n["sonota_man"]:
    fail("求職理由の内訳の合計が合わない")
jukyu_man = d["nenpo"]["jukyu_2024_sen"] / 10
rate = round(jukyu_man / n["shitsugyo_2024_man"] * 100, 1)
not_man = round(n["shitsugyo_2024_man"] - jukyu_man, 1)
if not (20 <= rate < 30):
    fail(f"受給の割合が「4人に1人」の範囲にない: {rate}%")
over6 = round(s["pct"]["m6_12"] + s["pct"]["y1"], 1)

# 3. 解説ページの数字・引用が data と合っているか
page_raw = (ROOT / "hoken-setsumei.html").read_text(encoding="utf-8")
page = squash(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", "", page_raw, flags=re.S)))
page_quotes = [d["nenpo"]["quote"], d["nendo"]["quote_total"], d["shosai"]["quote"], d["kaisei"]["quote_kakudai"],
               d["hw"]["quote_byouki"], "離職の日以前2年間に、被保険者期間（※補足2）が通算して12か月以上"]
for q in page_quotes:
    if squash(q) not in page:
        fail(f"解説ページに引用がない: {q[:40]}…")
if squash("離職の日以前2年間に、被保険者期間（※補足2）が通算して12か月以上") not in src["hw"]:
    fail("12か月以上の引用が写しにない")
page_nums = [f"{n['shitsugyo_2024_man']}万人", f"{jukyu_man}万人", f"約{round(not_man)}万人", f"{rate}%",
             f"{n['yameta_man']}万人", f"{n['arata_man']}万人", f"（{n['gakusotsu_man']}万人）", f"（{n['shunyu_man']}万人）",
             f"約{d['kaisei']['man_10_19h']}万人", "2028年10月", f"{d['days']['min']}日〜{d['days']['max']}日",
             f"{s['y1_man']}万人（{s['pct']['y1']}%）", f"{s['pct']['over3']}%", f"{s['shitsugyosha_man']}万人",
             f"{d['nenpo']['kotoshi_kyufu_2024_sen'] / 10}万人"]
for x in page_nums:
    if squash(x) not in page:
        fail(f"解説ページに数字がない（または違う）: {x}")
for w, want in [("24.4", rate), ("42.4", n["arata_man"] / n["yameta_man"] * 100)]:
    if abs(float(w) - want) > 0.05 or f'data-w="{w}"' not in page_raw:
        fail(f"棒の長さが合わない: {w} / {want:.1f}")

# 4. ツールに埋め込んだ数字が data と同じか
tool = (ROOT / "motsu.html").read_text(encoding="utf-8")
emb = json.loads(re.search(r"const P = (\{.*?\});", tool).group(1))
if emb != {"over3": s["pct"]["over3"], "over6": over6, "y1": s["pct"]["y1"]}:
    fail(f"ツールの割合が data と違う: {emb}")
m = re.search(r"const TAIKI = (\d+), SEIGEN = (\d+);", tool)
if not m or (int(m.group(1)), int(m.group(2))) != (d["hw"]["taiki_days"], d["kaisei"]["seigen_days"]):
    fail("ツールの待期・給付制限が data と違う")
if "gcUse('何か月もつしらべ')" not in tool:
    fail("ツールに利用回数の計測がない")


# 5. 試算を同じ決まりで計算し直す（Playwright でツールの simulate と突き合わせる表）
def simulate(save_man, cost_man, ins, day_yen=0, days=0, how=""):
    per_day = cost_man * 10000 / 30
    bal, start, stop = save_man * 10000, 0, 0
    if ins == "yes":
        start = d["hw"]["taiki_days"] + (d["kaisei"]["seigen_days"] if how == "jibun" else 0)
        stop = start + days
    for day in range(36 * 30):
        if ins == "yes" and start <= day < stop:
            bal += day_yen
        bal -= per_day
        if bal < 0:
            return math.ceil((day + 1) / 30)
    return None


CASES = [(0, 12, "no"), (50, 15, "no"), (100, 20, "no"), (500, 10, "no"),
         (30, 15, "yes", 5000, 90, "jibun"), (30, 15, "yes", 5000, 90, "kaisha"), (100, 20, "yes", 7000, 150, "kaisha")]
expect = [[*c, simulate(*c)] for c in CASES]
# 手計算で確かめた例: 貯金50万円・生活費15万円・失業保険なし → 50÷15＝3.33か月 → 4か月目に尽きる
if simulate(50, 15, "no") != 4 or simulate(0, 12, "no") != 1:
    fail("試算の手計算の例と合わない")

if errors:
    print("合わないところがあります:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: 引用{len(quotes)}件・件数{sum(map(len, must.values()))}件・解説の数字{len(page_nums)}件・ツールの数字が一致（受給 {rate}%・受けていない 約{not_man}万人・6か月以上 {over6}%）")
print("試算の答え（Playwright で突き合わせる）:", json.dumps(expect, ensure_ascii=False))
