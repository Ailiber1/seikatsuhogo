"""止まるラインの解説（teishi-setsumei.html）とツール（teishi.html）を、原本と照合する。

1. 引用（blockquote）が、生活保護法の条文（data/teishi_law.json）・実施要領の原本PDF（2段組みを左右に分けて読む）にそのままあるか
2. ツールの計算（CALC部分）の calcKijun・kisoKojo が、貯金の境目しらべ・給料いくら残るしらべの計算と同じ文か（それぞれ別の verify で確認済み）
3. 家賃の上限の取り出し（jutakuLimit）が、貯金の境目しらべの計算と全地域で同じ値を返すか
4. 「止まる目安」（stopLine）が、Python で1円ずつ数えて探した値と一致するか（ランダムな世帯・家賃・天引きで）
5. 解説に書いた金額が、独立に計算した値と同じか
6. 計測・作成者表記・リンク先が入っているか

使い方: python3 scripts/verify_teishi.py
"""
import json, re, html, subprocess, random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
norm = lambda s: re.sub(r"\s+", "", s)
ok = ng = 0
def check(c, label):
    global ok, ng
    if c: ok += 1
    else: ng += 1; print("不一致:", label)
load = lambda name: json.loads((DATA / name).read_text(encoding="utf-8"))

def pdf_cols(path):
    info = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True).stdout
    w, h = map(float, re.search(r"Page size:\s+([\d.]+) x ([\d.]+)", info).groups())
    pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
    out = []
    for p in range(1, pages + 1):
        for x in (0, w / 2):
            out.append(subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-x", str(int(x)), "-y", "0", "-W", str(int(w / 2)), "-H", str(int(h)), str(path), "-"],
                                      capture_output=True, text=True).stdout)
    return norm("".join(out))

tool_t = (ROOT / "scripts" / "teishi.template.html").read_text(encoding="utf-8")
tool = (ROOT / "teishi.html").read_text(encoding="utf-8")
doc = (ROOT / "teishi-setsumei.html").read_text(encoding="utf-8")
calc = re.search(r"// CALC-START\n(.*?)// CALC-END", tool_t, re.S).group(1)

# 1. 引用
law = load("teishi_law.json")["articles"]
law_text = norm("".join("".join(a["paragraphs"]) for a in law.values()))
pdf_text = pdf_cols(DATA / "jisshi_yoryo_r8_source.pdf")
for name, t in (("解説", doc), ("ツール", tool)):
    qs = [norm(html.unescape(re.sub(r"<[^>]+>", "", q))) for q in re.findall(r"<blockquote>(.*?)</blockquote>", t, re.S)]
    check(len(qs) >= 2, name + " の引用の数")
    for q in qs:
        check(q in law_text or q in pdf_text, name + " の引用が原本にない: " + q[:40])
check("保護は、厚生労働大臣の定める基準により測定した要保護者の需要を基とし" in norm(law["8"]["paragraphs"][0]), "第8条第1項")

# 2. 計算の関数が、検証済みの他ツールと同じ文か
def func(src, name):
    m = re.search(r"function " + name + r"\(.*?\n}\n", src, re.S)
    return norm(m.group(0)) if m else None
chokin_t = (ROOT / "scripts" / "chokin.template.html").read_text(encoding="utf-8")
kyuryo_t = (ROOT / "scripts" / "kyuryo.template.html").read_text(encoding="utf-8")
check(func(calc, "calcKijun") is not None and func(calc, "calcKijun") == func(chokin_t, "calcKijun"), "calcKijun が貯金の境目しらべと同じ")
check(func(calc, "kisoKojo") is not None and func(calc, "kisoKojo") == func(kyuryo_t, "kisoKojo"), "kisoKojo が給料いくら残るしらべと同じ")

# 3〜5. node で動かして比べる
kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
jutaku = {k: v for k, v in load("jutaku_limit.json").items() if k in ("pref", "city", "later_core_cities")}
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}
T = {k: v for k, v in load("kiso_kojo.json").items() if k in ("rows", "over")}
AGES = ["0～2", "3～5", "6～11", "12～17", "18～19", "20～40", "41～59", "60～64", "65～69", "70～74", "75～"]
random.seed(20261115)
cases = []
for _ in range(240):
    p = random.choice(list(kyuchi))
    c, lv = random.choice(kyuchi[p])
    n = random.randint(1, 5)
    ages = [random.choice(AGES) for _ in range(n)]
    cases.append({"p": p, "c": c, "lv": lv, "ages": ages, "rent": random.choice([0, 0, 20000, 35000]), "jippi": random.choice([0, 0, 5000, 18000])})
chokin_calc = re.search(r"function jutakuLimit\(.*?\n}\n", chokin_t, re.S).group(0)
js = calc + "\n" + chokin_calc.replace("function jutakuLimit(", "function jutakuLimitOld(").replace("JUTAKU", "JJ") + f"""
const K = {json.dumps(kijun, ensure_ascii=False)}, KE = {json.dumps(keika, ensure_ascii=False)}, J = {json.dumps(jutaku, ensure_ascii=False)}, T = {json.dumps(T, ensure_ascii=False)};
const JJ = J;
const cases = {json.dumps(cases, ensure_ascii=False)};
const out = cases.map(c => {{
  const n = c.ages.length, life = calcKijun(c.ages, c.lv, true, K, KE).total;
  const lim = jutakuLimit(J, c.p, c.c, c.lv, n), limOld = jutakuLimitOld(c.p, c.c, c.lv, n);
  const house = c.rent > 0 ? Math.min(c.rent, lim) : lim, M = life + house;
  return {{life, lim, limOld, M, G: stopLine(M, c.jippi, T)}};
}});
console.log(JSON.stringify(out));
"""
res = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)
check(all(r["lim"] == r["limOld"] for r in res), "家賃の上限の取り出しが貯金の境目しらべと同じ")

# Python で独立に基礎控除を数え直し、1円ずつ探して比べる
def kiso(x):
    if x >= T["over"]["from"]:
        return T["rows"][-1][2] + T["over"]["add_first"] * ((x - T["over"]["from"]) // T["over"]["step"] + 1)
    for a, b, v, _ in T["rows"]:
        if a <= x <= b: return x if v is None else v
def line(M, j):
    # 1円ずつ数えて、「最後にまだ届かない給料」を探し、その次の1円を返す
    last = -1
    for x in range(0, M + j + 120000):
        if max(0, x - min(x, j) - kiso(x)) < M: last = x
    return last + 1
bad = 0
for c, r in zip(cases[:60], res[:60]):
    if line(r["M"], c["jippi"]) != r["G"]: bad += 1
check(bad == 0, "止まる目安が1円ずつ数えた値と一致（60世帯）")
check(all(r["G"] > r["M"] for r in res), "止まる目安は最低生活費より大きい")
# 目安の直前（1円少ない）は保護が残り、目安は保護がゼロ
def hogo(M, x, j): return max(0, M - max(0, x - min(x, j) - kiso(x)))
check(all(hogo(r["M"], r["G"], c["jippi"]) == 0 and hogo(r["M"], r["G"] - 1, c["jippi"]) > 0 for c, r in zip(cases, res)), "目安ちょうどで保護費0・1円少ないと残る（240世帯）")
check(all(hogo(r["M"], x, c["jippi"]) == 0 for c, r in zip(cases[:40], res[:40]) for x in range(r["G"], r["G"] + 12000)), "目安以上なら、そのあとずっと保護費0（40世帯×1万2千円ぶん）")

# 5. 解説の金額が、ひとり暮らし（20〜40歳）の独立計算と同じか
ex = {"札幌市": ("北海道", "札幌市"), "長崎市": ("長崎県", "長崎市"), "東京23区": ("東京都", "千代田区")}
js2 = calc + f"""
const K = {json.dumps(kijun, ensure_ascii=False)}, KE = {json.dumps(keika, ensure_ascii=False)}, J = {json.dumps(jutaku, ensure_ascii=False)}, T = {json.dumps(T, ensure_ascii=False)};
const KY = {json.dumps({p: dict(kyuchi[p]) for p in ('北海道', '長崎県', '東京都')}, ensure_ascii=False)};
console.log(JSON.stringify({json.dumps(ex, ensure_ascii=False)} && Object.entries({json.dumps(ex, ensure_ascii=False)}).map(([nm,[p,c]]) => {{ const lv = KY[p][c], life = calcKijun(["20～40"], lv, true, K, KE).total, lim = jutakuLimit(J, p, c, lv, 1), M = life + lim; return [nm, life, lim, M, stopLine(M, 0, T)]; }})));
"""
rows = json.loads(subprocess.run(["node", "-e", js2], capture_output=True, text=True, check=True).stdout)
text = norm(html.unescape(re.sub(r"<[^>]+>", " ", doc)))
for nm, life, lim, M, G in rows:
    check(f"{M:,}円" in text and f"{G:,}円" in text, f"解説の{nm}の最低生活費{M:,}円・目安{G:,}円")
    check(line(M, 0) == G and G - kiso(G) >= M, f"{nm} の目安が式（最低生活費＋基礎控除）どおり")
    check(f"{G / 10000:.1f}万円" in text, f"{nm} の約{G / 10000:.1f}万円")
nagasaki = [r for r in rows if r[0] == "長崎市"][0]
check(f"{nagasaki[1]:,}円" in text and f"{nagasaki[2]:,}円" in text, "長崎市の生活費・家賃の上限")
# 長崎市は2級地-1（解説に書いた）
check(dict(kyuchi["長崎県"])["長崎市"] == 2, "長崎市は2級地-1")
# 長崎市の最低生活費は、給料いくら残るしらべの例（109,930円）と同じ
check(nagasaki[3] == 109930, "長崎市の最低生活費が給料いくら残るしらべの例（109,930円）と同じ")

# 6. 計測・作成者・リンク
check("data-goatcounter" in tool and "data-goatcounter" in doc, "計測が入っている")
check("gcUse('止まるラインしらべ')" in tool, "利用回数の呼び出し")
check("作成：" in tool and "作成：" in doc, "作成者表記")
for page, t in (("tool", tool), ("doc", doc)):
    for href in set(re.findall(r'href="([a-z0-9\-]+\.html)"', t)):
        check((ROOT / href).exists(), f"{page} の内部リンク先がある: {href}")
check("どこにも送信していません。ページが開かれた回数と結果が出た回数だけは、Cookieを使わず、個人を特定しない方法で数えています。" in tool, "ツールの注意書き")

print(f"\n一致 {ok} 件 / 不一致 {ng} 件")
raise SystemExit(1 if ng else 0)
