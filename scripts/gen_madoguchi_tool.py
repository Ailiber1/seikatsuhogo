"""相談窓口の検索ツール(sodan.html)を生成する。データを埋め込む。"""
import json
import re

S = "/private/tmp/claude-501/-private-tmp/4b42560e-3aa8-4bc5-8b88-2482dc59f9cb/scratchpad"
src = json.load(open(f"{S}/madoguchi.json", encoding="utf-8"))
DATA, SLUG = src["data"], src["slugs"]
PREF_ORDER = list(SLUG.values())
# スラッグを都道府県名→スラッグに反転（出典ページへのリンク用）
REV = {v: k for k, v in SLUG.items()}

def norm_city(c):
    """改行・全角スペースを整え、表示しやすい市区町村名にする。"""
    c = c.replace("\u3000", " ").replace("\n", "・").strip()
    c = re.sub(r"[・\s]*・[・\s]*", "・", c)   # 改行由来の「・・」を1つに
    c = re.sub(r"\s+", " ", c).strip("・ ")
    return c


def with_parent_city(city, office):
    """区名だけの行に、親となる市名を補う。
    例: 札幌市の窓口は自治体名の欄が区名の羅列なので「札幌市（中央区・…）」にする。
    これをしないと、利用者が「札幌市」で探しても見つからない。"""
    if re.search(r"[市町村]", city):
        return city                      # すでに市町村名が入っている
    for src in (office[0], office[1]):   # 窓口名 → 住所 の順に市名を探す
        m = re.search(r"([^\s、,。（(]{2,6}市)", src)
        if m:
            return f"{m.group(1)}（{city}）"
    return city


# 同じ市区町村名の窓口をまとめる: {都道府県: [[市区町村, [窓口...]], ...]}
compact = {}
for p in PREF_ORDER:
    rows = DATA.get(p) or []
    grouped = {}
    for x in rows:
        c = norm_city(x["city"])
        grouped.setdefault(c, []).append([x["name"], x["addr"], x["tel"].replace("\n", "／"), x["mail"]])
    if grouped:
        compact[p] = [[with_parent_city(c, v[0]), v] for c, v in grouped.items()]
total = sum(len(w) for v in compact.values() for _, w in v)

html = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>生活の相談窓口をさがす</title>
<style>
:root{
  --ground:#ffffff; --panel:#f6f8fb; --ink:#1b2430; --sub:#5b6673;
  --navy:#1e5388; --navy-soft:#e8f0f8; --on-navy:#ffffff;
  --ok:#16704a; --ok-bg:#e8f5ef;
  --line:#dde3ea; --line-soft:#eef1f5;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --ground:#14171c; --panel:#1c2027; --ink:#e8ecf1; --sub:#9aa4b0;
    --navy:#7fb0e6; --navy-soft:#1e2a38; --on-navy:#12161b;
    --ok:#5cc196; --ok-bg:#16302a;
    --line:#333a44; --line-soft:#252b33;
  }
}
:root[data-theme="dark"]{
  --ground:#14171c; --panel:#1c2027; --ink:#e8ecf1; --sub:#9aa4b0;
  --navy:#7fb0e6; --navy-soft:#1e2a38; --on-navy:#12161b;
  --ok:#5cc196; --ok-bg:#16302a;
  --line:#333a44; --line-soft:#252b33;
}
*{box-sizing:border-box}
body{background:var(--ground); color:var(--ink); margin:0;
  font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN","Yu Gothic Medium","Meiryo",system-ui,sans-serif;
  font-size:16px; line-height:1.75; -webkit-text-size-adjust:100%}
.mincho{font-family:"Hiragino Mincho ProN","Yu Mincho","YuMincho",serif}
.wrap{max-width:660px; margin:0 auto; padding:0 18px; padding-block:28px 40px}

header{border-bottom:2px solid var(--navy); padding-bottom:16px; margin-bottom:22px}
h1{font-size:clamp(25px,5.6vw,34px); line-height:1.35; margin:0 0 9px; font-weight:700;
   color:var(--navy); text-wrap:balance}
.lede{font-size:15.5px; color:var(--sub); margin:0}

.for-who{background:var(--navy); color:var(--on-navy); border-radius:11px; padding:13px 17px; margin:14px 0 0}
.for-who b{display:block; font-size:12.5px; letter-spacing:.06em; opacity:.85; margin-bottom:4px}
.for-who p{margin:0; font-size:16px; font-weight:700; line-height:1.6}

.fields{display:flex; flex-wrap:wrap; gap:11px; margin-bottom:11px}
.field{flex:1 1 200px; min-width:0}
label.cap{display:block; font-size:12.5px; color:var(--sub); margin-bottom:4px; letter-spacing:.02em}
select{width:100%; font:inherit; font-size:16px; color:var(--ink); background:var(--panel);
  border:1.5px solid var(--line); border-radius:8px; padding:11px 34px 11px 12px; appearance:none; cursor:pointer;
  background-image:linear-gradient(45deg,transparent 50%,var(--sub) 50%),linear-gradient(135deg,var(--sub) 50%,transparent 50%);
  background-position:calc(100% - 18px) 50%,calc(100% - 13px) 50%;
  background-size:5px 5px,5px 5px; background-repeat:no-repeat}
select:focus-visible{outline:2.5px solid var(--navy); outline-offset:1px}
.live-note{font-size:13px; color:var(--sub); margin:0 0 7px; text-align:center}
button.go{display:block; width:100%; margin:0; font:inherit; font-size:17px; font-weight:700;
  color:var(--on-navy); background:var(--navy); border:none; border-radius:9px; padding:14px;
  cursor:pointer; letter-spacing:.06em}
button.go:hover{filter:brightness(1.12)}
button.go:focus-visible{outline:2.5px solid var(--ink); outline-offset:2px}

.result{margin-top:24px}
.eg-bar{background:var(--ink); color:var(--ground); font-size:13.5px; line-height:1.6;
  padding:9px 15px; border-radius:11px 11px 0 0}
.eg-bar b{font-size:14.5px}
.hit{background:var(--panel); border:3px solid var(--ok); border-radius:13px; overflow:hidden}
.hit.with-bar{border-radius:0 0 13px 13px; border-top-width:0}
.hit-top{background:var(--ok-bg); padding:16px 18px}
.hit-place{font-size:13.5px; color:var(--sub); margin:0 0 3px}
.hit-name{font-size:clamp(18px,3.8vw,23px); font-weight:700; line-height:1.4; margin:0 0 9px; color:var(--ok)}
.multi{margin:6px 0 0; font-size:14px; color:var(--ink)}
.hit-body{padding:15px 18px}
.office + .office{margin-top:16px; padding-top:16px; border-top:2px dashed var(--line)}
dl{display:grid; grid-template-columns:5em 1fr; gap:8px 13px; margin:0; font-size:15.5px}
dt{color:var(--sub); font-weight:700; font-size:14px}
dd{margin:0; word-break:break-word}
dd a{color:var(--navy); font-weight:700}
.tel{font-size:19px; font-weight:700; font-variant-numeric:tabular-nums; letter-spacing:.01em}
.free{display:inline-block; font-size:11.5px; font-weight:700; background:var(--ok); color:var(--panel);
  border-radius:4px; padding:1px 7px; margin-left:6px; vertical-align:2px}
.links{margin-top:15px; padding-top:13px; border-top:1px solid var(--line); display:flex; flex-direction:column; gap:8px}
.links a{display:inline-flex; align-items:center; gap:7px; font-size:14px; color:var(--navy);
  background:var(--navy-soft); border-radius:6px; padding:9px 12px; text-decoration:none; font-weight:700; line-height:1.5}
.links a:hover{text-decoration:underline}
.none{background:var(--panel); border:3px solid var(--line); border-radius:13px; padding:16px 18px}
.none h3{margin:0 0 7px; font-size:18px}
.note{font-size:13.5px; color:var(--sub); line-height:1.7; margin-top:14px}

footer{margin-top:28px; padding-top:18px; border-top:1px solid var(--line);
  font-size:12.5px; color:var(--sub); line-height:1.8}
footer h2{font-size:14px; color:var(--ink); margin:0 0 7px; font-weight:700}
footer ul{margin:0 0 12px; padding-left:1.2em}
footer a{color:var(--navy); word-break:break-all}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="wrap">

<header>
  <h1 class="mincho">生活の相談窓口をさがす</h1>
  <p class="lede">生活保護の申請が不安なとき、福祉事務所より先に相談できる場所です。国の制度にもとづく窓口で、全国どの自治体にもあり、相談は無料です。</p>
  <div class="for-who">
    <b>こんなときに</b>
    <p>家族に知られたくない／うまく説明できる自信がない／そもそも生活保護を受けられるのか分からない</p>
  </div>
</header>

<div class="fields">
  <div class="field"><label class="cap" for="pref">都道府県</label><select id="pref"></select></div>
  <div class="field"><label class="cap" for="city">市区町村</label><select id="city"></select></div>
</div>
<p class="live-note">選ぶたびに、下の結果がその場で変わります。</p>
<button class="go" id="go">窓口を見る　↓</button>

<div class="result" id="result"></div>

<footer>
  <h2>このページのデータ</h2>
  <ul>
    <li>【一次】厚生労働省「生活困窮者自立支援制度」<br>
      <a href="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000059425.html" target="_blank" rel="noopener noreferrer">https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000059425.html</a></li>
    <li>窓口の一覧は、上の厚生労働省のページが案内している「令和7年度 自立相談支援機関窓口情報」から取得しました（全国__TOTAL__か所）<br>
      <a href="https://minna-tunagaru.jp/ichiran/" target="_blank" rel="noopener noreferrer">https://minna-tunagaru.jp/ichiran/</a></li>
  </ul>
  <h2>読むときの注意</h2>
  <p>窓口の名前・住所・電話番号は移転や統合で変わることがあります。<b>行く前に電話で確かめてください。</b></p>
  <p><b>市区町村の欄にご自分の市名が見当たらないとき。</b>札幌市・大阪市・横浜市など大きな市は、<b>市名ではなく区名</b>（北区、中央区など）で並んでいます。ご自分の区名を探してください。近隣の町村がまとめて1つの窓口になっていることもあります。それでも見つからない場合は、市区町村の役所にお問い合わせください。</p>
  <p>選んだ内容はこの画面の中だけで処理していて、どこにも送信していません。確認日：2026年9月23日</p>
</footer>

</div>

<script>
const DATA = __DATA__;
const SLUG = __SLUG__;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

const PREFS = Object.keys(DATA);
$("pref").innerHTML = PREFS.map(p => `<option>${p}</option>`).join("");

function fillCities(){
  const list = DATA[$("pref").value] || [];
  $("city").innerHTML = list.map(([c],i) => `<option value="${i}">${esc(c)}</option>`).join("");
}

function telHtml(tel){
  return String(tel).split("／").filter(Boolean).map(t => {
    const digits = t.replace(/[^0-9]/g, "");
    const free = /^(0120|0800)/.test(digits) ? '<span class="free">フリーダイヤル</span>' : "";
    return `<span class="tel">${esc(t)}</span>${free}`;
  }).join("<br>");
}

function show(isExample){
  const pref = $("pref").value;
  const rows = DATA[pref] || [];
  const entry = rows[+$("city").value] || rows[0];
  const slug = SLUG[pref] || "";
  const listUrl = `https://minna-tunagaru.jp/ichiran/${slug}/`;
  if(!entry){
    $("result").innerHTML = `<div class="none"><h3>この都道府県のデータがありません</h3>
      <p>お住まいの市区町村の役所にお問い合わせください。</p></div>`;
    return;
  }
  const [city, offices] = entry;
  const bar = isExample
    ? '<div class="eg-bar"><b>これは例です。</b>配信者が実際に相談した窓口を出しています。上で選び直すと、あなたの地域に変わります。</div>'
    : "";
  const count = offices.length > 1
    ? `<p class="multi">この地域には <b>${offices.length}か所</b> あります。行きやすいところで大丈夫です。</p>` : "";
  const cards = offices.map(([name, addr, tel, mail]) => `
    <div class="office">
      <p class="hit-name">${esc(name)}</p>
      <dl>
        <dt>電話</dt><dd>${telHtml(tel) || "―"}</dd>
        <dt>住所</dt><dd>${esc(addr) || "―"}</dd>
        ${mail ? `<dt>メール</dt><dd><a href="mailto:${esc(mail)}">${esc(mail)}</a></dd>` : ""}
        <dt>費用</dt><dd>無料</dd>
      </dl>
    </div>`).join("");
  $("result").innerHTML = `
    ${bar}
    <div class="hit ${isExample ? "with-bar" : ""}">
      <div class="hit-top">
        <p class="hit-place">${esc(pref)} ${esc(city)} の相談窓口</p>
        ${count}
      </div>
      <div class="hit-body">
        ${cards}
        <div class="links">
          <a href="${listUrl}" target="_blank" rel="noopener noreferrer">厚生労働省が案内している一覧で確認する（${esc(pref)}）</a>
          <a href="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000059425.html" target="_blank" rel="noopener noreferrer">この窓口の制度について（厚生労働省）</a>
        </div>
        <p class="note">まず電話で「生活が苦しくて相談したい」と伝えれば大丈夫です。生活保護を申請すると決めていなくても相談できます。</p>
      </div>
    </div>`;
}

$("pref").addEventListener("change", () => { fillCities(); show(); });
$("city").addEventListener("change", () => show());
$("go").addEventListener("click", () => {
  show();
  $("result").scrollIntoView({behavior:"smooth", block:"start"});
});

// 初期表示：配信者が実際に相談した窓口を例として出す
$("pref").value = "長崎県";
fillCities();
const i = (DATA["長崎県"] || []).findIndex(([c]) => c === "長崎市");
if(i >= 0) $("city").value = i;
show(true);
</script>
</body>
</html>
"""

html = (html
        .replace("__DATA__", json.dumps(compact, ensure_ascii=False, separators=(",", ":")))
        .replace("__SLUG__", json.dumps(REV, ensure_ascii=False, separators=(",", ":")))
        .replace("__TOTAL__", f"{total:,}"))

out = f"{S}/repo3/sodan.html"
open(out, "w", encoding="utf-8").write(html)
print("生成:", out, len(html.encode()), "bytes ／ 窓口", total, "件")
