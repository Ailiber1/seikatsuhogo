"""「やってはいけないこと」の解説（yatte-setsumei.html）とツール（shinkoku.html）を検算する。

1. 引用（<blockquote>）が、原本の写し（生活保護法・次官通知・課長通知）の本文に入っているか（「…」で区切って各部分を照合）
2. 資料の数字が、data/kitakyushu_fusei.json から計算した値と合っているか
3. ツールの引用が次官通知の写しに入っているか、計算（しきい値）が決まりどおりか
4. 北九州市のページ自体の不整合（発見の契機の合計）が、資料の注意書きと合っているか

使い方: python3 scripts/verify_yatte.py   （間違いがあれば、その場で止まる）
"""
import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"


def norm(s):
    s = H.unescape(s)
    s = s.replace("(", "(").replace(")", ")")
    return re.sub(r"\s+", "", s)


def strip_html(p):
    t = p.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t)
    return norm(re.sub(r"<[^>]+>", "", t))


law = json.loads((D / "yatte_law.json").read_text(encoding="utf-8"))
law_text = norm("".join("".join(a["paragraphs"]) for a in law["articles"].values()))
jikan = strip_html(D / "jikan_tsuchi_dai8_source.html")
kacho = strip_html(D / "kacho_tsuchi_dai3_source.html")
corpus = {"法": law_text, "次官通知": jikan, "課長通知": kacho}
ng = []


def find_in_any(q):
    parts = [norm(x) for x in re.split(r"…", q) if norm(x)]
    for name, text in corpus.items():
        if all(p in text for p in parts):
            return name
    return None


page = (ROOT / "yatte-setsumei.html").read_text(encoding="utf-8")
quotes = [re.sub(r"<[^>]+>", "", q) for q in re.findall(r"(?s)<blockquote>(.*?)</blockquote>", page)]
print(f"資料の引用: {len(quotes)}か所")
for q in quotes:
    where = find_in_any(q)
    if where is None:
        ng.append(f"原本に見つからない引用: {q[:60]}…")
print("  → 原本の本文に入っているか確認しました" if not [x for x in ng if x.startswith("原本")] else "")

# --- 北九州市の数字 ---
k = json.loads((D / "kitakyushu_fusei.json").read_text(encoding="utf-8"))
Y = k["years"]
last = Y[-1]
tot = k["count_amount"][last]["count"]
amt = k["count_amount"][last]["amount"]
all_tot = sum(k["kinds"]["合計"])
kinds = k["kinds"]
trig = k["trigger"]
wage_last = kinds["稼働収入 小計"][-1]
other_last = kinds["稼働収入以外 小計"][-1]
rest_last = kinds["扶助費 小計"][-1] + kinds["その他 小計"][-1]
wage_all = sum(kinds["稼働収入 小計"])
pct = lambda a, b: round(a / b * 100)
expect = {
    f"{tot}": True,  # 303
    f"{all_tot:,}件": True,  # 2,081件
    f"{amt:,}円": True,
    f"{wage_last}件（{pct(wage_last, tot)}%）": True,
    f"{other_last}件（{pct(other_last, tot)}%）": True,
    f"{rest_last}件（{pct(rest_last, tot)}%）": True,
    f"{wage_all:,}件で、全体の{pct(wage_all, all_tot)}%": True,
    f"{trig['福祉事務所の調査'][-1]}件（{pct(trig['福祉事務所の調査'][-1], tot)}%）": True,
    f"{trig['課税状況調査'][-1]}件（{pct(trig['課税状況調査'][-1], tot)}%）": True,
    f"{trig['住民等からの通報・投書'][-1]}件（{pct(trig['住民等からの通報・投書'][-1], tot)}%）": True,
    f"任意保険金等の無申告が{kinds['任意保険金等の無申告'][-1]}件": True,
    f"年金・福祉各法の給付の無申告が{kinds['各種年金及び福祉各法に基づく給付の無申告'][-1]}件": True,
    f"世帯員の増減・転居の無届」で見つかったのは<b>8年間で{sum(kinds['世帯員の増減・転居の無届'])}件": True,
    f"預貯金等の無申告は{kinds['預貯金等の無申告'][-1]}件、資産収入の無申告は{kinds['資産収入の無申告'][-1]}件": True,
}
for s in expect:
    if s not in page:
        ng.append(f"資料に次の数字・文がない（データと合わない）: {s}")
# 棒の長さ（最大を100%とした相対値）
bar_expect = [
    (wage_last, wage_last), (other_last, wage_last), (rest_last, wage_last),
    (trig["福祉事務所の調査"][-1], trig["福祉事務所の調査"][-1]), (trig["課税状況調査"][-1], trig["福祉事務所の調査"][-1]),
    (trig["住民等からの通報・投書"][-1], trig["福祉事務所の調査"][-1]),
]
widths = [int(w) for w in re.findall(r'style="--w:(\d+)%"', page)]
want_w = [round(a / b * 100) for a, b in bar_expect]
if widths != want_w:
    ng.append(f"棒の長さが合わない: 資料 {widths} / 計算 {want_w}")
# 発見の契機の合計
if sum(trig[n][-1] for n in ["住民等からの通報・投書", "関係機関からの通報・照会", "監査及び検査の指摘", "課税状況調査", "福祉事務所の調査", "その他"]) != tot:
    ng.append("令和7年度の発見の契機の内訳が合計と合わない")
mm = k.get("trigger_sum_mismatch", {})
for y, v in mm.items():
    if y in ("令和2年度", "令和3年度") and (str(v["sum"]) not in page or str(v["total"]) not in page):
        ng.append(f"{y}の不整合の数字が資料の注意書きにない")
if set(mm) - {"令和2年度", "令和3年度"}:
    ng.append(f"資料に書いていない年度で契機の合計が合わない: {set(mm)}")
if last in mm:
    ng.append("令和7年度の契機の合計が合わない（資料の前提が崩れている）")

# --- ツール ---
tool = (ROOT / "shinkoku.html").read_text(encoding="utf-8")
s = json.loads((D / "shinkoku.json").read_text(encoding="utf-8"))
print(f"ツールの引用: {len(s['items']) + 1}か所")
for it in s["items"]:
    if norm(it["quote"]) not in jikan:
        ng.append(f"ツールの引用が次官通知の写しに見つからない: {it['id']}")
    if norm(it["quote"]) not in norm(tool.replace("\\", "")) and it["quote"] not in tool:
        # 埋め込みはJSONなので、エスケープなしでそのまま入る
        ng.append(f"ツールHTMLに引用が埋め込まれていない: {it['id']}")
    if it["calc"] == "excess":
        m = re.search(r"(\d{1,2},\d{3})円", it["quote"])
        if not m or int(m.group(1).replace(",", "")) != it["threshold"]:
            ng.append(f"しきい値が引用と合わない: {it['id']}")
if norm(s["common_quote"]["text"]) not in jikan:
    ng.append("ツールの共通の引用が次官通知の写しに見つからない")

# 計算（counted と同じ式）を総当たりで確かめる
def counted(it, amt):
    if it["calc"] == "excess":
        return max(0, amt - it["threshold"])
    if it["calc"] == "full":
        return amt
    return None


cases = {("rinji", 8000): 0, ("rinji", 10000): 2000, ("rinji", 3000): 0, ("small", 15000): 0, ("small", 20000): 5000, ("pension", 50000): 50000, ("gift", 3000): 3000, ("rent", 30000): 30000, ("wage", 50000): None}
byid = {it["id"]: it for it in s["items"]}
for (i, a), want in cases.items():
    if counted(byid[i], a) != want:
        ng.append(f"計算が合わない: {i} {a} → {counted(byid[i], a)} （正しくは {want}）")
# ブラウザ側の式が同じか（テンプレートの文字列を確認）
tpl = (ROOT / "scripts" / "shinkoku.template.html").read_text(encoding="utf-8")
for frag in ["Math.max(0, amt - it.threshold)", "if (it.calc === 'full') return amt;"]:
    if frag not in tpl:
        ng.append(f"ブラウザ側の式が検算の式と違う: {frag}")

if ng:
    print("\n".join("NG: " + x for x in ng))
    sys.exit(1)
print("OK: 引用・数字・棒の長さ・ツールの計算は、すべて原本とデータに合っています")
