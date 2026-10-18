"""「労働収入の一部を引かれずに貯められる」解説（nokoseru-setsumei.html）と、働いたら残せるお金しらべ（nokoseru.html）を照合する。

- data/nokoseru.json の引用が、通知の写し（法令等データベースのHTML）にそのまま入っているか
- 解説ページに書いた引用・数字が data と合っているか
- ツールの基礎控除が data/kiso_kojo.json の表どおりか、就労自立給付金の計算が通知の決まりどおりかを、ここで計算し直した答えの表として出す（Playwright で突き合わせる）

使い方: python3 scripts/verify_nokoseru.py
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
d = json.loads((DATA / "nokoseru.json").read_text(encoding="utf-8"))
kiso = json.loads((DATA / "kiso_kojo.json").read_text(encoding="utf-8"))
errors = []
fail = errors.append
squash = lambda s: re.sub(r"\s+", "", unicodedata.normalize("NFKC", s))


def html_text(p):
    b = p.read_bytes()
    for enc in ("utf-8", "cp932"):
        try:
            t = b.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    return re.sub(r"<[^>]+>", " ", t)


src = {k: squash(html_text(DATA / v["copy"])) for k, v in d["sources"].items()}
quotes = [("jikan", d["rinji"]["quote"]), ("jikan", d["jiritsu"]["quote_head"]), ("jikan", d["jiritsu"]["quote_kashitsuke"]),
          ("jikan", d["jiritsu"]["quote_keiyo"]), ("kyokucho", d["jiritsu"]["quote_yoto"]), ("kyokucho", d["jiritsu"]["quote_keikaku"]),
          ("kacho", d["jiritsu"]["quote_seigyo"]), ("shuro", d["shuro"]["quote_santei"]), ("shuro", d["shuro"]["quote_kikan"]),
          ("shuro", d["shuro"]["quote_jogen"]), ("shuro", d["shuro"]["quote_shushi"])]
for k, q in quotes:
    if squash(q) not in src[k]:
        fail(f"引用が写しにない（{k}）: {q[:40]}…")
s = d["shuro"]
if (s["rate_pct"], s["add_tanshin"], s["add_fukusu"], s["max_tanshin"], s["max_fukusu"]) != (10, 20000, 30000, 100000, 150000):
    fail("就労自立給付金の数字が引用と合わない")


def kojo(income, first=True):
    """基礎控除額（月額）。kiso_kojo.json の表どおり。収入が表の上限を超えたら4,000円ごとに加算"""
    for lo, hi, a, b in kiso["rows"]:
        if lo <= income <= hi:
            v = a if first else b
            return income if v is None else v
    o = kiso["over"]
    steps = (income - o["from"]) // o["step"] + 1
    last = kiso["rows"][-1][2 if first else 3]
    return last + steps * (o["add_first"] if first else o["add_second"])


def kyufukin(monthly_juto, months, single=True):
    """就労自立給付金。各月の収入充当額×10%（1円未満切り捨て）の合計＋単身2万円/複数3万円、上限10万円/15万円"""
    total = sum(int(m * s["rate_pct"] / 100) for m in [monthly_juto] * min(months, s["months"]))
    total += s["add_tanshin"] if single else s["add_fukusu"]
    return min(total, s["max_tanshin"] if single else s["max_fukusu"])


CASES = [10000, 15199, 15200, 30000, 50000, 80000, 100000, 150000, 230000, 250000]
expect = []
for g in CASES:
    k = kojo(g)
    juto = g - k
    expect.append([g, k, juto, kyufukin(juto, 6, True), kyufukin(juto, 6, False)])
# 手計算の例: 給料10万円 → 控除23,600円（99,000〜102,999円の行）→ 認定76,400円 → ×10%×6か月＝45,840円＋2万円＝65,840円
if kojo(100000) != 23600 or kyufukin(100000 - 23600, 6) != 65840 or kyufukin(500000, 6) != 100000:
    fail("手計算の例と合わない")

page_p = ROOT / "nokoseru-setsumei.html"
if page_p.exists():
    page = squash(html_text(page_p))
    for k, q in quotes:
        if q in (d["shuro"]["quote_kikan"], d["jiritsu"]["quote_head"], d["jiritsu"]["quote_kashitsuke"]):  # 期間・見出し・借りたお金は本文で言いかえている
            continue
        if squash(q) not in page:
            fail(f"解説ページに引用がない: {q[:40]}…")
    for x in ["15,200円", "10万円", "15万円", "2万円", "6か月", "8,000円", "18,400円", "31,600円", "38,960円"]:
        if squash(x) not in page:
            fail(f"解説ページに数字がない: {x}")
tool_p = ROOT / "nokoseru.html"
if tool_p.exists():
    tool = tool_p.read_text(encoding="utf-8")
    emb = json.loads(re.search(r"const K = (\{.*?\});", tool).group(1))
    if emb["rows"] != kiso["rows"] or emb["over"] != {k: kiso["over"][k] for k in ("from", "step", "add_first", "add_second")}:
        fail("ツールの基礎控除の表が kiso_kojo.json と違う")
    if "gcUse('残せるお金しらべ')" not in tool:
        fail("ツールに利用回数の計測がない")

if errors:
    print("合わないところがあります:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print(f"OK: 引用{len(quotes)}件が写しと一致。基礎控除と就労自立給付金の計算の答え（Playwright で突き合わせる）:")
print(json.dumps(expect))
