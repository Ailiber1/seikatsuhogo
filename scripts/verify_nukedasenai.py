"""nukedasenai-setsumei.html の数字が data/nukedasenai.json（国の表から計算し直したもの）と合うか、
引用した条文が e-Gov の本文と同じかを確かめる。合わなければ止まる。
使い方: python3 -I scripts/extract_nukedasenai.py && python3 -I scripts/verify_nukedasenai.py [e-Govの法令JSONを置いたフォルダ]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "data", "nukedasenai.json"), encoding="utf-8"))
html = open(os.path.join(ROOT, "nukedasenai-setsumei.html"), encoding="utf-8").read()
text = re.sub(r"<[^>]+>", "", html)
c, t = d["calc"], d["haishi_by_type"]["総数"]
kiso = json.load(open(os.path.join(ROOT, "data", "kiso_kojo.json"), encoding="utf-8"))

ng = []


def has(s, why):
    if s not in text:
        ng.append(f"{why}: 「{s}」がページにない")


def comma(n):
    return f"{n:,}"


has(comma(c["haishi_total"]) + "世帯", "やめた世帯の総数")
has(comma(c["dead"]) + "世帯", "死亡")
has(f'{c["dead_pct"]}%は「死亡」', "死亡の割合")
has(comma(c["work"]) + "世帯（" + f'{c["work_pct"]}%', "働いてやめた")
has(comma(c["cure"]) + "世帯（" + f'{c["cure_pct"]}%', "傷病治癒")
has(f'{c["dead_70plus_pct"]}%は世帯主が70歳以上', "死亡のうち70歳以上")
has(f'65歳以上まで入れると{c["dead_65plus_pct"]}%', "死亡のうち65歳以上")
for k in ["その他", "失そう", "社会保障給付金の増加"]:
    has(f'{comma(t[k])}世帯（{round(t[k] / t["総数"] * 100, 1)}%）', "やめた理由 " + k)
for a, v in c["work_pct_by_age"].items():
    if a in ("19歳以下",):
        continue
    has(a.replace("～", "〜") + f"{v}%", "年齢別 " + a)
has(comma(c["again_total"]) + "世帯", "また受け始めた世帯")
has(f'{c["again_within1y_pct"]}%は、やめてから1年たたずに', "1年以内に戻った割合")
has(f'{comma(c["again_under3m"])}世帯（{c["again_under3m_pct"]}%）', "3か月未満")
has(f'（{c["again_reason_chokin_pct"]}%）', "戻った理由 貯金")
has(f'（{c["again_share_of_kaishi_pct"]}%）', "開始世帯に占める割合")
has(comma(d["n6_r6"]["保護開始世帯数"]) + "世帯", "年間の開始世帯")
p = d["saijukyu_by_period"]
mid = sum(p[k]["総数"] for k in ["３月～６月未満", "６月～１年未満"])
mid2 = sum(p[k]["総数"] for k in ["１年～２年未満", "２年～３年未満", "３年～４年未満", "４年～５年未満"])
has(f'{comma(mid)}世帯（{round(mid / c["again_total"] * 100, 1)}%）', "3か月〜1年未満")
has(f'{comma(mid2)}世帯（{round(mid2 / c["again_total"] * 100, 1)}%）', "1年〜5年未満")
has(f'{comma(p["５年以上"]["総数"])}世帯（{round(p["５年以上"]["総数"] / c["again_total"] * 100, 1)}%）', "5年以上")

# 基礎控除：月10万円・1人目
row = next(r for r in kiso["rows"] if r[0] <= 100000 <= r[1])
has(comma(row[2]) + "円が手元に残る", "10万円の基礎控除")
has(comma(100000 - row[2]) + "円は、保護費から差し引かれます", "10万円のうち引かれる額")

# 条文（e-Gov の法令JSONを置いたフォルダが渡されたときだけ）
if len(sys.argv) > 1:
    def law_text(p):
        def txt(n):
            if isinstance(n, str):
                return n
            if isinstance(n, dict):
                return "".join(txt(x) for x in n.get("children", []))
            if isinstance(n, list):
                return "".join(txt(x) for x in n)
            return ""
        return txt(json.load(open(p))["law_full_text"])
    kokuho = law_text(os.path.join(sys.argv[1], "law_333AC0000000192.json"))
    nenkin = law_text(os.path.join(sys.argv[1], "law_334AC0000000141.json"))
    for q in re.findall(r"<blockquote>(.*?)</blockquote>", html, re.S):
        for part in re.sub(r"<[^>]+>", "\n", q).split("\n"):
            part = re.sub(r"^[一二三四五六七八九十]+　", "", part.strip())
            if part and part not in kokuho and part not in nenkin:
                ng.append("引用が条文にない: " + part[:40])

if ng:
    print("\n".join(ng))
    raise SystemExit(1)
print("ok: 数字と引用はすべて data・条文と一致")
