"""data/shitsugyo.json（失業給付の決まり）と、級地・経過的加算・基準額・住宅扶助の上限・基礎控除額表を埋め込んで
shitsugyo.html（失業・低収入チェック）を生成する。

使い方: python3 scripts/gen_shitsugyo_tool.py
生成後に python3 scripts/verify_shitsugyo.py で、日数の表・1日の額の計算式・生活扶助と基礎控除の計算を確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

shitsugyo = load("shitsugyo.json")
shitsugyo = {k: shitsugyo[k] for k in ("kihon", "other_support")}
kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
jutaku = {k: v for k, v in load("jutaku_limit.json").items() if k in ("pref", "city", "later_core_cities")}
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}
kiso = {k: v for k, v in load("kiso_kojo.json").items() if k in ("rows", "over", "other")}

html = (ROOT / "scripts" / "shitsugyo.template.html").read_text(encoding="utf-8")
for key, obj in (("SHITSUGYO", shitsugyo), ("KYUCHI", kyuchi), ("KEIKA", keika), ("KIJUN", kijun), ("JUTAKU", jutaku), ("KISO", kiso)):
    html = html.replace(f"/*{key}*/", dump(obj))
(ROOT / "shitsugyo.html").write_text(add_snippet(html), encoding="utf-8")
print("shitsugyo.html を生成しました")
