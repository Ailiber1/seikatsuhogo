"""解説（naiwake-setsumei.html）とクイズ（naiwake-quiz.html）の数字を、data/naiwake.json に入れた国の表の件数から計算し直して確かめる。

1. 原本に書いてある割合（55.2%・84.7%・34.5%など）が、件数から計算した値と合うか
2. 自分で計算した割合（20代・30代 8.0%、19歳以下 8.1%、100世帯の図の内訳）が正しく、図の点の合計が100か
3. ページに書いた数字と引用が data/naiwake.json と合っているか
4. クイズの正解の選択肢が、数字と矛盾していないか／結果のひとこと（SCORE）が正解数どおりに出るか

使い方: python3 scripts/verify_naiwake.py
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
read = lambda name: (ROOT / name).read_text(encoding="utf-8")
d = json.loads(read("data/naiwake.json"))
doc, quiz_html = read("naiwake-setsumei.html"), read("naiwake-quiz.html")
bad = []
pct = lambda a, b: round(a / b * 100, 1)

# 1. 毎月の調査（2026年7月）
m = d["monthly_2026_07"]
for name, (n, p) in m["types"].items():
    if pct(n, m["total"]) != p: bad.append(("月次の割合", name, pct(n, m["total"]), p))
if sum(n for n, _ in m["types"].values()) != m["total"]: bad.append(("月次の合計", sum(n for n, _ in m["types"].values())))
if pct(m["elderly_single"][0], m["total"]) != m["elderly_single"][1]: bad.append(("高齢単身",))

# 年に1回の調査（2024年7月末）
y = d["nenji_2024_07"]
tw = y["types_work"]
if sum(v["work"] + v["nowork"] for v in tw.values()) != y["households"]: bad.append(("年次の世帯合計",))
for name, v in tw.items():
    if pct(v["work"], v["work"] + v["nowork"]) != v["work_pct"]: bad.append(("就労の割合", name, pct(v["work"], v["work"] + v["nowork"]), v["work_pct"]))
if sum(v["work"] for v in tw.values()) != y["work_households"][0] or pct(y["work_households"][0], y["households"]) != y["work_households"][1]: bad.append(("就労世帯",))
if sum(y["age"].values()) != y["persons"]: bad.append(("年齢の合計", sum(y["age"].values())))
a65 = y["age"]["65～69歳"] + y["age"]["70歳以上"]
if pct(a65, y["persons"]) != y["age65_pct"]: bad.append(("65歳以上", pct(a65, y["persons"])))
if pct(y["period_5y_plus"][0], y["households"]) != y["period_5y_plus"][1]: bad.append(("5年以上",))

# 2. 自分で計算した割合
young = y["age"]["20～29歳"] + y["age"]["30～39歳"]
kids = y["age"]["0～19歳"]
calc = {"20代・30代": (pct(young, y["persons"]), "8.0%"), "19歳以下": (pct(kids, y["persons"]), "8.1%")}
for k, (v, s) in calc.items():
    if f"{v:.1f}%" != s or s not in doc: bad.append(("試算", k, v))
if f"{young // 10000}万{young % 10000:,}人" not in doc: bad.append(("20代30代の人数", young))
# 100世帯の図: 5つの内訳を、合計が100になるように丸める（端数の大きい順に1ずつ足す）
hh = lambda name: tw[name]["work"] + tw[name]["nowork"]
parts = [("old", hh("高齢者世帯")), ("sick", hh("障害者・傷病者世帯")), ("mom", hh("母子世帯")),
         ("work", tw["その他の世帯"]["work"]), ("none", tw["その他の世帯"]["nowork"])]
share = [(k, n / y["households"] * 100) for k, n in parts]
fig = {k: int(float(n)) for k, n in re.findall(r"\{k: '(\w+)',\s+n: (\d+),", doc)}
if sum(fig.values()) != 100: bad.append(("図の点の合計", sum(fig.values())))
for k, s in share:
    if abs(fig.get(k, -9) - s) >= 1: bad.append(("図の点", k, fig.get(k), round(s, 1)))
for s in ("55.8%", "24.3%", "3.6%", "5.6%", "10.6%"):
    if s not in doc: bad.append(("図の注記", s))
got = [f"{v:.1f}%" for _, v in share]
if got != ["55.8%", "24.3%", "3.6%", "5.6%", "10.6%"]: bad.append(("図の内訳の計算", got))

# 3. ページの数字・引用
for s in ["55.2%", "25.6%", "15.8%", "3.4%", "34.5%", "46.7%", "52.5%", "84.7%", "62.7%", "69.6%", "9年6か月", "47.3%", "17.8%", "17.7%",
          "196万9,655人", "164万4,102世帯", "162万6,840世帯", "197万8,439人", y["quotes"]["work"], y["quotes"]["one"], d["start_reason_r5"]["quote"]]:
    if s not in doc: bad.append(("解説に無い", s[:24]))
for q in d["quiz"]:
    if q["q"] not in quiz_html or q["say"] not in quiz_html: bad.append(("クイズに無い", q["k"]))

# 4. クイズの正解と数字。選択肢の言葉から範囲を決めて、数字がその中に入っているか
rng = {"ほぼ0": (0, 3), "1割より少ない": (0, 10), "1割くらい": (5, 15), "2割くらい": (15, 25), "3割くらい": (25, 35), "3割以上": (30, 50), "4割くらい": (35, 45),
       "5割くらい": (45, 55), "5割以上": (50, 70), "半分以上": (50, 100), "6割以上": (60, 80), "7割くらい": (65, 75), "7割以上": (70, 100), "8割以上": (80, 100), "9割以上": (90, 100)}
want = {"elderly": m["types"]["高齢者世帯"][1], "young": calc["20代・30代"][0], "one": y["one_person_pct"], "work": tw["その他の世帯"]["work_pct"], "period": y["period_5y_plus"][1]}
for q in d["quiz"]:
    if q["pct"] != want[q["k"]] or q["label"] != f"{q['pct']:.1f}%": bad.append(("クイズの数字", q["k"], q["pct"], want[q["k"]]))
    fits = [c for c in q["choices"] if rng[c][0] <= q["pct"] < rng[c][1]]
    if fits != [q["choices"][q["answer"]]]: bad.append(("正解の選択肢が1つに決まらない", q["k"], fits))

sc = re.search(r"// SCORE-START(.*?)// SCORE-END", quiz_html, re.S).group(1)
js = sc + "const Q=[0,1,2,3,4].map(a=>({answer:a}));console.log(JSON.stringify([[0,1,2,3,4],[0,1,2,9,9],[0,9,9,9,9],[9,9,9,9,9]].map(p=>score(p,Q).right)))"
with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
    f.write(js)
if json.loads(subprocess.run(["node", f.name], capture_output=True, text=True, check=True).stdout) != [5, 3, 1, 0]: bad.append(("正解数の数え方",))

print("国の表の件数から計算し直した割合・図の内訳・ページの数字と引用・クイズの正解:", "すべて一致" if not bad else "")
for b in bad:
    print("不一致:", b)
sys.exit(1 if bad else 0)
