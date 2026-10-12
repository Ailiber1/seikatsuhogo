"""data/naiwake.json のクイズ（国の調査の数字つき）を埋め込んで naiwake-quiz.html（生活保護イメージ当てクイズ）を生成する。

使い方: python3 scripts/gen_naiwake_quiz.py
生成後に python3 scripts/verify_naiwake.py で、クイズと解説の数字が国の表の件数から計算した値と合っているか確かめる。
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_snippet import add_snippet  # 利用回数の計測（GoatCounter）

ROOT = Path(__file__).resolve().parent.parent
d = json.loads((ROOT / "data" / "naiwake.json").read_text(encoding="utf-8"))
dump = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

# 選択肢の正解番号が範囲に入っているか・出典の名前が合っているか
for q in d["quiz"]:
    if not (0 <= q["answer"] < len(q["choices"])) or q["src"] not in d["sources"]:
        sys.exit(f"クイズの定義がおかしい: {q['k']}")

html = (ROOT / "scripts" / "naiwake-quiz.template.html").read_text(encoding="utf-8")
html = html.replace("/*QUIZ*/", dump(d["quiz"])).replace("/*SOURCES*/", dump({k: {"name": v["name"], "url": v["url"]} for k, v in d["sources"].items()}))
(ROOT / "naiwake-quiz.html").write_text(add_snippet(html), encoding="utf-8")
print("naiwake-quiz.html を生成しました（", len(d["quiz"]), "問）")
