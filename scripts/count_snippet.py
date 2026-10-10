"""利用回数の計測（GoatCounter）を、全ページの </head> の直前に入れる。

- 数えるのは「ページが開かれた回数」と、ツールで結果が出た回数（gcUse('ツール名') → 「利用/ツール名」）だけ。
  入力した内容（市区町村・金額など）は送らない。Cookie は使わない。
- 読み込むスクリプトは版を固定し、改ざん防止の指紋（SRI）を付ける。版を上げるときは指紋も計算し直す:
    curl -s https://gc.zgo.at/count.v5.js | openssl dgst -sha384 -binary | base64
- 自分の利用を数えないようにするには、そのブラウザで一度だけ
    https://ailiber1.github.io/seikatsuhogo/#toggle-goatcounter
  を開く（GoatCounter の標準機能。ブラウザごとに必要）。

使い方: python3 scripts/count_snippet.py   … リポジトリ直下の全 .html に入れる（入っていれば何もしない）
        gen_*.py からは add_snippet(html) を呼ぶ
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARK = "data-goatcounter"
SNIPPET = """<script>
/* URLの後ろの ?… は付けず、ページの場所だけで数える（同じページが別々に数えられないように） */
window.goatcounter = {path: function () { return location.pathname; }};
</script>
<script data-goatcounter="https://liber-seiho.goatcounter.com/count" async src="https://gc.zgo.at/count.v5.js" crossorigin="anonymous" integrity="sha384-atnOLvQb9t+jTSipvd75X2yginT4PjVbqDdlJAmxMm+wYElFmeR6EmLP5bYeoRVQ"></script>
<script>
/* ツールで結果が出たときに1回だけ「利用/ツール名」を数える。入力した内容は送らない */
window.gcUse = function (name) {
  window.gcUse.done = window.gcUse.done || {};
  if (window.gcUse.done[name]) return;
  window.gcUse.done[name] = true;
  var tries = 0;
  (function send() {
    if (window.goatcounter && window.goatcounter.count) {
      window.goatcounter.count({path: '利用/' + name, title: name, event: true});
    } else if (tries++ < 20) {
      setTimeout(send, 500);
    }
  })();
};
</script>
"""


# ページどうしをつなぐ部品（related.js）。本文の最後に入れる。まとめサイト（index.html）は自分で hub-items.js を読むので入れない
RELATED_TAG = '<script src="hub-items.js"></script>\n<script src="related.js" defer></script>\n'


def add_related(html: str) -> str:
    if "related.js" in html:
        return html
    i = html.lower().rfind("</body>")
    return html + RELATED_TAG if i < 0 else html[:i] + RELATED_TAG + html[i:]


def add_snippet(html: str) -> str:
    html = add_related(html)
    if MARK in html:
        return html
    i = html.lower().find("</head>")
    if i < 0:
        # <head> を書かない形のページ（tokurei.html）は、最初の </style> の直後（本文より前）に入れる
        j = html.lower().find("</style>")
        if j < 0:
            raise ValueError("</head> も </style> も見つからない")
        i = j + len("</style>\n")
    return html[:i] + SNIPPET + html[i:]


if __name__ == "__main__":
    missing = []
    for p in sorted(ROOT.glob("*.html")):
        s = p.read_text(encoding="utf-8")
        t = s if p.name == "index.html" else add_snippet(s)
        if t != s:
            p.write_text(t, encoding="utf-8")
            print("追加:", p.name)
        if MARK not in t:
            missing.append(p.name)
        if p.name != "index.html" and "related.js" not in t:
            missing.append(p.name + "（related.js）")
    print("計測が入っていないページ:", missing or "なし")
    sys.exit(1 if missing else 0)
