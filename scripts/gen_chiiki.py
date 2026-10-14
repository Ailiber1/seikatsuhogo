"""地域の暮らしやすさの資料（chiiki-setsumei.html）とツール（chiiki.html）を生成する。

使い方: python3 scripts/rank_chiiki.py && python3 scripts/gen_chiiki.py
資料の数字は、手で書かずに全部ここでデータから計算して差し込む（書き写しの誤りを防ぐ）。
生成後に python3 scripts/verify_chiiki.py で、ツールの計算が保護費しらべ・rank_chiiki.py と一致するか確かめる。
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）
import rank_chiiki as rk

ROOT = Path(__file__).resolve().parent.parent
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
yen = lambda n: f"{round(n):,}"
esc = html.escape
norm = lambda name: name.replace("ヶ", "ケ").replace("　", "").strip()  # extract_chiiki.py と同じ

R = json.loads((ROOT / "data" / "chiiki_rank.json").read_text(encoding="utf-8"))
C = R["cities"]
ch, bag = rk.ch, rk.bag
GOMI_CODE = {"有料": 0, "無料": 1, "一部有料": 2, "収集無し": 3}
by = lambda k, rev=False: sorted(C, key=lambda c: (C[c][k], c), reverse=rev)


def bars(rows, vmax=None):
    """rows: [(ラベル, 小さい説明, 値, 表示, 'ng'|'ok'|'')]。0から始まる横棒（差を大きく見せない）"""
    vmax = vmax or max(r[2] for r in rows)
    out = []
    for lb, sm, v, disp, cls in rows:
        if lb is None:
            out.append('<div class="gap"></div>')
            continue
        out.append(f'<div class="row {cls}"><span class="lb">{esc(lb)}{f"<small>{esc(sm)}</small>" if sm else ""}</span>'
                   f'<span class="tr"><i data-w="{v / vmax * 100:.1f}"></i></span><span class="v">{disp}</span></div>')
    return '<div class="hb">' + "".join(out) + "</div>"


F = {}
F["CHECKED"] = "2026年10月15日"
order = sorted(C, key=lambda c: (C[c]["rank"], c))
assert C[order[0]]["rank"] == 1 and C[order[-1]]["rank"] == 52, (order[0], order[-1])
F["TOP1"] = order[0]
F["LAST1"] = order[-1]

kb = bag["北見市"]
F["KITAMI_BAG_YEAR"] = yen(kb["yen"] * 2 * 52)

# 2章: 級地ごとの生活扶助（ひとり暮らし・20〜40歳）
fj = [rk.seikatsu_fujo(["20～40"], lv) for lv in range(6)]
kit_lv = rk.kyuchi["北海道"]["北見市"]
assert kit_lv == 4
F["SVG_KYUCHI"] = bars([(rk.LV[lv], "北見市" if lv == kit_lv else ("東京23区・大阪市など" if lv == 0 else ""), fj[lv], yen(fj[lv]) + "円",
                         "ng" if lv == kit_lv else "") for lv in range(6)])
F["FUJO_DIFF"] = yen(fj[0] - fj[5])
F["FUJO_DIFF_Y"] = yen((fj[0] - fj[5]) * 12)
F["KITAMI_FUJO_DIFF"] = yen(fj[0] - fj[kit_lv])

areas = {}
for p in ch["price_pref"]:
    areas.setdefault(ch["touki"]["pref_area"].get(p, 6), []).append(p)
tk = {a: ch["touki"]["amount"][str(a)][0] * ch["touki"]["months"][str(a)] for a in range(1, 7)}
area_lbl = {a: ("・".join(x if x == "北海道" else x[:-1] for x in areas[a]) if a < 6 else "東京・大阪など（その他）") for a in range(1, 7)}
F["SVG_TOUKI"] = bars([(rk.AREA[a], area_lbl[a], tk[a], yen(tk[a]) + "円", "ok" if a == 1 else "") for a in range(1, 7)])
F["TOUKI1_Y"] = yen(tk[1])
F["TOUKI6_Y"] = yen(tk[6])

# 3章: 物価
pp = ch["price_pref"]
yn = {p: v["yachin_nozoku"] for p, v in pp.items()}
yn_order = sorted(yn, key=lambda p: -yn[p])
assert yn_order[0] == "北海道"
F["P_HOKKAIDO"] = f'{yn["北海道"]:.1f}'
F["P_TOKYO"] = f'{yn["東京都"]:.1f}'
F["P_TOKYO_RANK"] = str(1 + sum(1 for p in yn if yn[p] > yn["東京都"]))
assert max(pp, key=lambda p: pp[p]["konetsu"]) == "北海道"
F["P_HOKKAIDO_KONETSU"] = f'{pp["北海道"]["konetsu"]:.1f}'
muni = []
for p, cs in rk.kyuchi.items():
    for c, lv in cs.items():
        muni.append((round(rk.seikatsu_fujo(["20～40"], lv) / (yn[p] / 100)), p, c, lv))
F["N_MUNI"] = f"{len(muni):,}"
lo = min(m[0] for m in muni)
lows = [m for m in muni if m[0] == lo]
assert all(m[1] == "北海道" and m[3] == 5 for m in lows), lows[:3]
F["N_LOWEST"] = str(len(lows))
F["LOWEST_VAL"] = yen(lo)
hi = max(m[0] for m in muni)
his = [m for m in muni if m[0] == hi]
F["HIGHEST_NAME"] = "・".join(m[1] + m[2] for m in his)
F["HIGHEST_VAL"] = yen(hi)
F["MUNI_GAP"] = yen(hi - lo)

# 4章: 光熱費
nat = R["national"]
F["TOYU_AOMORI"] = yen(C["青森市"]["toyu"])
F["TOYU_NAT"] = yen(ch["kakei"]["全国"]["toyu"])
F["TOYU_RATIO"] = f'{C["青森市"]["toyu"] / ch["kakei"]["全国"]["toyu"]:.1f}'
assert max(C, key=lambda c: C[c]["toyu"]) == "青森市"
m2 = by("m2")
show = m2[:3] + [None] + [c for c in ("札幌市", "青森市") if c not in m2[:3] + m2[-5:]] + [None] + m2[-5:]
rows = []
for c in show:
    if c is None:
        rows.append((None, None, 0, "", ""))
        continue
    rows.append((c, f'光熱費{yen(C[c]["konetsu"])}−加算{yen(C[c]["touki2_year"])}', C[c]["m2"], yen(C[c]["m2"]) + "円",
                 "ng" if c in m2[-5:] else ("ok" if c in m2[:3] else "")))
F["SVG_KONETSU"] = bars(rows)
F["KON_SAPPORO"] = yen(C["札幌市"]["konetsu"])
F["TOUKI_SAPPORO"] = yen(C["札幌市"]["touki2_year"])
F["KON2_SAPPORO"] = yen(C["札幌市"]["m2"])
F["R2_SAPPORO"] = f'{C["札幌市"]["r2"]:g}'
F["M2_WORST"] = f'{m2[-1]}（{yen(C[m2[-1]]["m2"])}円・52位）'
F["M2_WORST5"] = "・".join(reversed(m2[-5:]))

# 5章: ガソリン
m3 = by("m3")
rows = [(c, "", C[c]["m3"], yen(C[c]["m3"]) + "円", "ok") for c in m3[:5]] + [(None, None, 0, "", "")] + \
       [(c, "", C[c]["m3"], yen(C[c]["m3"]) + "円", "ng") for c in m3[-5:]]
F["SVG_GAS"] = bars(rows)
F["GAS_MAX_CITY"], F["GAS_MAX"] = m3[-1], yen(C[m3[-1]]["m3"])
F["GAS_MIN_CITY"], F["GAS_MIN"] = m3[0], yen(C[m3[0]]["m3"])
F["GAS_RATIO"] = f'{C[m3[-1]]["m3"] / C[m3[0]]["m3"]:.1f}'

# 6章: ごみ袋
paid = [c for c in C if C[c]["gomi_status"] == "有料"]
F["GOMI_PAID_N"] = str(len(paid))
F["GOMI_NAT_PAID"] = f'{sum(1 for p in ch["gomi"].values() for v in p.values() if v["moyasu"] == "有料"):,}'
assert set(paid) | {"北見市"} == set(bag), set(paid) ^ set(bag)


def genmen_short(g):
    if not g:
        return '<span style="color:var(--sub)">未確認</span>'
    head = g.split("（")[0]
    return {"あり": '<b style="color:var(--ok)">あり</b>', "なし": "なし", "一部": "一部の人だけ"}.get(head, esc(head))


grows = []
for c in sorted(bag, key=lambda c: (-bag[c]["yen"] / bag[c]["liters"], c)):
    b = bag[c]
    per45 = b["yen"] / b["liters"] * 45
    label = f'<a href="{esc(b["src"])}" target="_blank" rel="noopener">{esc(c)}</a>' + ("<small class=\"blk\">52都市の外</small>" if c not in C else "") + ("<small>※</small>" if b.get("unofficial") else "")
    plus = "<small>＋袋代</small>" if "袋の代金" in (b.get("note", "") + b.get("since", "")) else ""
    grows.append(f'<tr><td class="c">{label}</td><td>{yen(b["yen"] * 10)}円<small class="blk">{b["liters"]}L{"・" + plus[7:-8] if plus else ""}</small></td><td>{yen(b["yen"] * 2 * 52)}円</td><td class="c w">{genmen_short(b.get("genmen", ""))}</td></tr>')
F["GOMI_TABLE"] = "".join(grows)
F["SAPPORO_BAG_YEAR"] = yen(bag["札幌市"]["yen"] * 2 * 52)

# 7章: 家賃の上限・水道
m5 = by("m5", rev=True)
F["M5_BEST"] = f'{m5[0]}（上限{yen(C[m5[0]]["jutaku1"])}円・住居の物価{C[m5[0]]["jukyo_idx"]:.1f}）'
F["M5_WORST"] = f'{m5[-1]}（上限{yen(C[m5[-1]]["jutaku1"])}円・住居の物価{C[m5[-1]]["jukyo_idx"]:.1f}）'
m6 = by("m6")
F["SUIDO_MAX_CITY"], F["SUIDO_MAX"] = m6[-1], yen(C[m6[-1]]["m6"])
F["SUIDO_MIN_CITY"], F["SUIDO_MIN"] = m6[0], yen(C[m6[0]]["m6"])
F["SUIDO_RATIO"] = f'{C[m6[-1]]["m6"] / C[m6[0]]["m6"]:.1f}'

# 8章: ランキング（上位10・下位10）
fr = lambda r: f"{r:g}"
rrows = []
for i, c in enumerate(order):
    if 10 <= i < len(order) - 10:
        if i == 10:
            rrows.append(f'<tr class="sep"><td colspan="8">（11位〜{len(order) - 10}位は省略）</td></tr>')
        continue
    v = C[c]
    cls = "good" if i < 10 else "bad"
    rrows.append(f'<tr class="{cls}"><td class="r c">{fr(v["rank"])}</td><td class="c">{esc(c)}</td>' +
                 "".join(f'<td>{fr(v["r" + str(k)])}</td>' for k in range(1, 7)) + "</tr>")
F["RANK_TABLE"] = "".join(rrows)

# 資料を書き出す
doc = (ROOT / "scripts" / "chiiki-setsumei.template.html").read_text(encoding="utf-8")
for k, v in F.items():
    doc = doc.replace(f"%%{k}%%", v)
left = re.findall(r"%%[A-Z0-9_]+%%", doc)
assert not left, left
(ROOT / "chiiki-setsumei.html").write_text(add_snippet(doc), encoding="utf-8")

# ツールを書き出す
kyuchi_rows = {p: [[c, lv, GOMI_CODE[ch["gomi"][p][norm(c)]["moyasu"]]] for c, lv in cs.items()]
               for p, cs in rk.kyuchi.items()}
r52 = {c: {k: v[k] for k in ("pref", "rank", "price", "m1", "m2", "m3", "m4", "m5", "m6")} for c, v in C.items()}
tool = (ROOT / "scripts" / "chiiki.template.html").read_text(encoding="utf-8")
repl = {
    "/*KYUCHI*/": dump(kyuchi_rows),
    "/*KEIKA*/": dump(rk.keika),
    "/*KIJUN*/": dump({k: v for k, v in rk.kijun.items() if k in ("dai1", "dai2", "teigen", "tokurei")}),
    "/*JUTAKU*/": dump({k: v for k, v in rk.jutaku.items() if k in ("pref", "city")}),
    "/*TOUKI*/": dump(ch["touki"]),
    "/*PRICE*/": dump({p: [v["yachin_nozoku"], v["jukyo"]] for p, v in pp.items()}),
    "/*R52*/": dump(r52),
    "/*BAG*/": dump(bag),
    "/*NAT*/": dump(nat),
    "/*CHECKED*/": F["CHECKED"],
}
for k, v in repl.items():
    assert k in tool, k
    tool = tool.replace(k, v)
(ROOT / "chiiki.html").write_text(add_snippet(tool), encoding="utf-8")
print("chiiki-setsumei.html と chiiki.html を生成しました")
print(json.dumps({k: v for k, v in F.items() if "TABLE" not in k and "SVG" not in k}, ensure_ascii=False, indent=0))
