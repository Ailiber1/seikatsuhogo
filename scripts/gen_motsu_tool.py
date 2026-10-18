"""data/shitsugyo_hoken.json の失業期間別の割合・待期・給付制限を埋め込んで motsu.html（失業したら、お金は何か月もつ？）を生成する。

使い方: python3 scripts/gen_motsu_tool.py
生成後に python3 scripts/verify_hoken.py で、数字が国の資料の写しと合っているか、試算が正しいかを確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "shitsugyo_hoken.json").read_text(encoding="utf-8"))
s, pct = d["shosai"], d["shosai"]["pct"]

# 割合は国の表のまま使う。6か月以上は「6か月～1年未満」＋「1年以上」の足し算
# 国の表は人数を四捨五入しているので、内訳の合計（50.7%）と「3か月以上」（51.2%）が0.5ずれる
period = {"over3": pct["over3"], "over6": round(pct["m6_12"] + pct["y1"], 1), "y1": pct["y1"]}
if abs(pct["m3"] + pct["over3"] - 100) > 0.05 or abs(pct["m3_6"] + pct["m6_12"] + pct["y1"] - pct["over3"]) > 0.6:
    sys.exit("失業期間の割合の合計が合わない")

src = d["sources"]
html = (ROOT / "scripts" / "motsu.template.html").read_text(encoding="utf-8")
for k, v in {
    "/*SEIDO*/": json.dumps({"hw_url": src["hw"]["url"], "kaisei_url": src["kaisei"]["page"],
                             "kyushokusha_url": d["seido"]["kyushokusha"]["url"], "kyushokusha_max": d["seido"]["kyushokusha"]["shisan_man"],
                             "jukyo_url": d["seido"]["jukyo"]["url"], "jukyo_max": d["seido"]["jukyo"]["chokin_max_man"]}, ensure_ascii=False),
    "/*PERIOD*/": json.dumps(period), "/*TAIKI*/": str(d["hw"]["taiki_days"]), "/*SEIGEN*/": str(d["kaisei"]["seigen_days"]),
    "/*SHOSAI_URL*/": src["shosai"]["url"], "/*HW_PROC_URL*/": src["hw_proc"]["url"], "/*KAISEI_URL*/": src["kaisei"]["page"],
    "/*M3*/": str(s["m3_man"]), "/*M3_6*/": str(s["m3_6_man"]), "/*M6_12*/": str(s["m6_12_man"]), "/*Y1*/": str(s["y1_man"]),
    "/*CHECKED*/": d["checked"].replace("-", "年", 1).replace("-", "月", 1) + "日",
}.items():
    if k not in html:
        sys.exit(f"ひな形に {k} がない")
    html = html.replace(k, v)
(ROOT / "motsu.html").write_text(add_snippet(html), encoding="utf-8")
print("motsu.html を生成しました", period)
