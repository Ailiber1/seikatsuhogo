/*
  YouTube動画を「押したら読み込む」形で置く部品。
  使い方: ページの好きな場所に次の1行を書き、末尾に <script src="video-embed.js" defer></script> を1回だけ置く。

    <div data-yt data-id="動画ID" data-title="動画の題名" data-label="動画でも解説しています"></div>

  - 最初は動画の絵（サムネイル）だけ出す。押すと youtube-nocookie.com の埋め込みに切り替わる
  - APIキーは使わない。動画が非公開・削除になると再生できなくなるので、IDを入れる前に公開状態を確認する
  - data-label は省略できる（省略すると題名だけ表示）
*/
(function () {
  var css =
    '.yt{margin:18px 0}' +
    '.yt-frame{position:relative;aspect-ratio:16/9;border-radius:16px;overflow:hidden;background:#111;border:2px solid #e2e7ec}' +
    '.yt-frame img,.yt-frame iframe{position:absolute;inset:0;width:100%;height:100%;border:0;object-fit:cover}' +
    '.yt-btn{position:absolute;inset:0;width:100%;height:100%;padding:0;border:0;background:none;cursor:pointer;display:block}' +
    '.yt-play{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:58px;height:58px;border-radius:50%;' +
    'background:rgba(20,28,38,.78);color:#fff;display:grid;place-items:center;font-size:20px;padding-left:4px;transition:transform .15s,background .15s}' +
    '.yt-btn:hover .yt-play,.yt-btn:focus-visible .yt-play{background:#2b5d8f;transform:translate(-50%,-50%) scale(1.08)}' +
    '.yt-btn:focus-visible{outline:3px solid #2b5d8f;outline-offset:-3px}' +
    '.yt-cap{margin:8px 2px 0;font-size:13px;line-height:1.55;color:#5f6a77}' +
    '.yt-cap b{display:block;color:#2b5d8f;font-size:12px;letter-spacing:.04em}';
  var st = document.createElement('style');
  st.textContent = css;
  document.head.appendChild(st);

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c];
    });
  }

  function mount(el) {
    var id = el.getAttribute('data-id');
    if (!/^[\w-]{11}$/.test(id || '')) return;
    var title = el.getAttribute('data-title') || '動画';
    var label = el.getAttribute('data-label');
    el.classList.add('yt');
    el.innerHTML =
      '<div class="yt-frame"><button type="button" class="yt-btn" aria-label="動画を再生する：' + esc(title) + '">' +
      '<img src="https://i.ytimg.com/vi/' + id + '/hqdefault.jpg" alt="" loading="lazy"><span class="yt-play">▶</span></button></div>' +
      '<p class="yt-cap">' + (label ? '<b>' + esc(label) + '</b>' : '') + esc(title) + '</p>';
    el.querySelector('.yt-btn').addEventListener('click', function () {
      el.querySelector('.yt-frame').innerHTML =
        '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' + esc(title) + '" ' +
        'allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>';
    });
  }

  window.ytMount = function (root) {
    (root || document).querySelectorAll('[data-yt]').forEach(mount);
  };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { window.ytMount(); });
  } else {
    window.ytMount();
  }
})();
