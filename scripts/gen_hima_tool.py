"""data/jikan_r3.json（国の生活時間の平均・平日）を埋め込んで hima.html（暇人スキャン）を生成する。

使い方: python3 scripts/extract_jikan.py （元データを作り直すときだけ）
        python3 scripts/gen_hima_tool.py
リスナーの結果は Firebase Realtime Database（プロジェクト seikatsuhogo）の /jikan/r に保存される。
書き込みのルールは database.rules.json（反映: firebase deploy --only database）。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
src = json.loads((ROOT / "data" / "jikan_r3.json").read_text(encoding="utf-8"))
keys = ["sleep", "work", "house", "meal", "free", "other"]
data = {}
for k, v in src["data"].items():
    day, sex, work, age = k.split("|")
    if day != "weekday" or work == "all" or age == "00":
        continue
    data[f"{sex}|{work}|{age}"] = [v[x] for x in keys] + [v["n"]]
jikan = {"ages": src["ages"], "data": data}
html = (ROOT / "scripts" / "hima.template.html").read_text(encoding="utf-8")
html = html.replace("/*JIKAN*/", json.dumps(jikan, ensure_ascii=False, separators=(",", ":")))
(ROOT / "hima.html").write_text(add_snippet(html), encoding="utf-8")
print("hima.html を生成しました（国の平均", len(data), "区分）")
