"""data/ の級地・経過的加算・基準額を埋め込んで hogohi.html（保護費しらべ）を生成する。

使い方: python3 scripts/gen_hogohi_tool.py
生成後に python3 scripts/verify_hogohi.py で、厚労省のモデル世帯54件との一致を確かめる。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
load = lambda name: json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

kyuchi = load("kyuchi_by_city.json")["data"]
keika = load("keika.json")["data"]
kijun = {k: v for k, v in load("kijun_r8.json").items() if k in ("dai1", "dai2", "teigen", "tokurei")}

html = (ROOT / "scripts" / "hogohi.template.html").read_text(encoding="utf-8")
html = html.replace("/*KYUCHI*/", dump(kyuchi)).replace("/*KEIKA*/", dump(keika)).replace("/*KIJUN*/", dump(kijun))
(ROOT / "hogohi.html").write_text(html, encoding="utf-8")
print("hogohi.html を生成しました（市区町村", sum(len(v) for v in kyuchi.values()), "件）")
