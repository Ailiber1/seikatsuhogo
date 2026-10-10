/*
  ページどうしをつなぐ部品。まとめサイト（index.html）以外の全ページが読み込む（scripts/count_snippet.py が自動で入れる）。

  1. ページの下に「あわせて読みたい」を出す。どのページに何を並べるかは、下の RELATED に書く。
     カードの絵・題名・説明は hub-items.js の ITEMS と同じものを使う。
  2. 本文の中の内部リンク（href="xxx.html"）のうち、鍵付き（hub-items.js で locked:true）のページへのものは、
     押せなくして「🔐 配信で公開予定」に置き換える。鍵を外す（locked:true を消す）と、どのリンクも自動で押せるようになる。
     ただし、いま開いているページ自体が鍵付きのときは、鍵付きページどうしのリンクは押せる（配信前の確認用）。

  新しいページを作ったら: hub-items.js に1行足し、ここの RELATED に「そのページ → 関連させるページ」を足す。
  関連は、読み終わった人が次に知りたくなる順に並べる（最大4つ）。相互に張るなら、相手側にも足す。
*/
(function () {
  var RELATED = {
    "shitsugyo-setsumei.html": ["hogohi.html", "chokin-setsumei.html", "kyuryo.html", "fuyo.html"],
    "shitsugyo.html":          ["hogohi.html", "chokin.html", "kyuryo.html", "shitsugyo-setsumei.html"],
    "chokin-setsumei.html":    ["chokin.html", "hogohi.html", "fuyo.html", "shitsugyo-setsumei.html"],
    "chokin.html":             ["chokin-setsumei.html", "hogohi.html", "fuyo.html", "sodan.html"],
    "fuyo.html":               ["sodan.html", "chokin-setsumei.html", "shitsugyo-setsumei.html", "anti.html"],
    "hogohi.html":             ["tokurei-setsumei.html", "kyuryo.html", "chokin.html", "shitsugyo.html"],
    "kyuryo.html":             ["hogohi.html", "shitsugyo.html", "hima-setsumei.html", "chokin.html"],
    "tokurei-setsumei.html":   ["tokurei.html", "hogohi.html", "tsuika-setsumei.html"],
    "tokurei.html":            ["tokurei-setsumei.html", "hogohi.html", "tsuika.html"],
    "tsuika-setsumei.html":    ["tsuika.html", "tokurei-setsumei.html", "hogohi.html"],
    "tsuika.html":             ["tsuika-setsumei.html", "tokurei.html", "hogohi.html"],
    "anti.html":               ["anti-kaeshi.html", "hima-setsumei.html", "shitsugyo-setsumei.html", "fuyo.html"],
    "anti-kaeshi.html":        ["anti.html", "hima-setsumei.html", "shitsugyo-setsumei.html"],
    "hima-setsumei.html":      ["hima.html", "anti.html", "kyuryo.html"],
    "hima.html":               ["hima-setsumei.html", "anti.html", "kyuryo.html"],
    "basic-income.html":       ["shitsugyo-setsumei.html", "hogohi.html", "hima-setsumei.html"],
    "jikohasan-setsumei.html": ["blacklist.html", "chokin-setsumei.html", "sodan.html", "fuyo.html"],
    "blacklist.html":          ["jikohasan-setsumei.html", "chokin-setsumei.html", "sodan.html"],
    "sodan.html":              ["fuyo.html", "chokin-setsumei.html", "shitsugyo-setsumei.html", "jikohasan-setsumei.html"]
  };

  var page = location.pathname.split("/").pop() || "index.html";
  var items = (typeof ITEMS !== "undefined") ? ITEMS : [];
  var by = {};
  items.forEach(function (i) { by[i.href] = i; });
  var meLocked = !!(by[page] && by[page].locked);
  var isLocked = function (href) { return !!(by[href] && by[href].locked) && !meLocked; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]; }); };

  // 1. 本文の中の内部リンク: 鍵付きページへのものは押せなくする
  document.querySelectorAll("a[href]").forEach(function (a) {
    var h = a.getAttribute("href");
    if (!/^[a-z0-9-]+\.html(#.*)?$/.test(h)) return;
    if (a.closest(".rel-box")) return;
    if (!isLocked(h.split("#")[0])) return;
    var s = document.createElement("span");
    s.className = "rel-locked";
    s.textContent = "🔐 配信で公開予定のページ";
    a.replaceWith(s);
  });

  // 2. あわせて読みたい
  var list = (RELATED[page] || []).filter(function (h) { return by[h] && h !== page; });
  if (!list.length) return;
  var css =
    ".rel-box{max-width:720px;margin:34px auto 0;padding:0 16px;font-family:inherit}" +
    ".rel-box h2{font-size:17px;margin:0 0 10px;color:#2b5d8f;font-family:inherit}" +
    ".rel-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}" +
    "@media (max-width:520px){.rel-grid{grid-template-columns:1fr}}" +
    ".rel-card{display:flex;gap:10px;align-items:flex-start;text-decoration:none;color:#242c36;border:1.5px solid #e2e7ec;border-radius:12px;padding:10px 12px;background:#fff;min-height:64px}" +
    ".rel-card:hover,.rel-card:focus-visible{border-color:#2b5d8f;background:#eef3f8}" +
    ".rel-card .ic{flex:none;font-size:24px;line-height:1.3}" +
    ".rel-card b{display:block;font-size:15px;line-height:1.45;color:#2b5d8f}" +
    ".rel-card small{display:block;font-size:12.5px;line-height:1.5;color:#5f6a77;margin-top:2px}" +
    ".rel-card .kd{display:inline-block;font-size:11px;font-weight:700;color:#5f6a77;border:1px solid #e2e7ec;border-radius:10px;padding:0 7px;margin-bottom:2px}" +
    ".rel-card.locked{border-style:dashed;background:#fafbfc;cursor:not-allowed}" +
    ".rel-card.locked .ic,.rel-card.locked b,.rel-card.locked small{opacity:.5;filter:grayscale(.6)}" +
    ".rel-locked{font-size:.92em;color:#5f6a77;font-weight:700;white-space:nowrap}" +
    ".rel-home{display:block;text-align:center;margin:14px 0 0;font-size:14px}.rel-home a{color:#2b5d8f;font-weight:700}";
  var st = document.createElement("style");
  st.textContent = css;
  document.head.appendChild(st);

  var cards = list.map(function (h) {
    var i = by[h], lock = isLocked(h);
    var kind = i.kind === "tool" ? "ツール" : "解説";
    if (lock) {
      return '<div class="rel-card locked" aria-disabled="true"><span class="ic">🔐</span><span><span class="kd">配信で公開</span><b>？？？</b><small>配信で公開します</small></span></div>';
    }
    return '<a class="rel-card" href="' + esc(i.href) + '"><span class="ic">' + i.icon + '</span><span><span class="kd">' + kind +
      '</span><b>' + esc(i.title) + '</b><small>' + esc(i.desc) + '</small></span></a>';
  }).join("");
  var box = document.createElement("section");
  box.className = "rel-box";
  box.innerHTML = "<h2>あわせて読みたい</h2><div class=\"rel-grid\">" + cards + "</div>" +
    '<p class="rel-home"><a href="./">生活保護のしらべもの 一覧へ</a></p>';
  var foot = document.querySelector(".foot");
  var main = document.querySelector("main") || document.body;
  if (foot && foot.parentNode) foot.parentNode.insertBefore(box, foot);
  else main.appendChild(box);
})();
