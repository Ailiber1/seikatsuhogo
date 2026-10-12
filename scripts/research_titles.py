"""他のチャンネルで伸びているタイトルを集めて、再生数の多い順に並べる（/seiho-week の下調べ用）。

- data/research_keywords.json の検索語で YouTube を検索し（1語につき30本）、参考チャンネルの新しい動画も足す
- ショート（90秒未満）と自分のチャンネルは除く。同じ動画は1回だけ数える
- ニュース番組のチャンネルは別枠に分ける（個人の暮らし・生き方系のタイトルの型を見たいので）
- YouTube Data API は使わない（yt-dlp だけ。APIの枠は配信中のチャット取得で使い切ることがあるため）

使い方:
  python3 scripts/research_titles.py                 … 表を表示
  python3 scripts/research_titles.py --json out.json … 結果をファイルにも保存
  python3 scripts/research_titles.py --add "検索語"   … その場で検索語を足して調べる（ファイルは書き換えない）

注意: 他チャンネルの再生数は、登録者数も公開からの日数も違う。「この型が通用している」という目安として使う。
"""
import argparse, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "data" / "research_keywords.json").read_text(encoding="utf-8"))
SEP = "\x1f"  # 題名に | が入ることがあるので、区切りは制御文字にする
FMT = SEP.join(["%(view_count)s", "%(channel)s", "%(duration)s", "%(id)s", "%(title)s"])


def ytdlp(target, extra=()):
    cmd = ["yt-dlp", "--flat-playlist", "--extractor-args", "youtube:lang=ja", "--print", FMT, *extra, target]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return [l.split(SEP) for l in r.stdout.splitlines() if l.count(SEP) == 4]


def num(s):
    try:
        return float(s)
    except ValueError:
        return None


def search(keyword, n=30):
    rows = []
    for v, ch, dur, vid, title in ytdlp(f"ytsearch{n}:{keyword}"):
        views, d = num(v), num(dur)
        if views is None or (d is not None and d < 90):
            continue
        rows.append({"views": int(views), "channel": ch, "id": vid, "title": title, "from": keyword})
    return rows


def channel_videos(ch, n=60):
    """チャンネルの新しい動画。日本語の題名と再生数は、同時には取れないので2回取りに行って合わせる"""
    ja = {vid: title for _, _, _, vid, title in ytdlp(ch["url"] + "/videos", ["--playlist-end", str(n)])}
    cmd = ["yt-dlp", "--flat-playlist", "--playlist-end", str(n), "--print", "%(view_count)s" + SEP + "%(duration)s" + SEP + "%(id)s", ch["url"] + "/videos"]
    rows = []
    for l in subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines():
        p = l.split(SEP)
        if len(p) != 3 or num(p[0]) is None or p[2] not in ja:
            continue
        d = num(p[1])
        if d is not None and d < 90:
            continue
        rows.append({"views": int(num(p[0])), "channel": ch["name"], "id": p[2], "title": ja[p[2]], "from": "参考チャンネル"})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--add", action="append", default=[])
    ap.add_argument("--top", type=int, default=60)
    a = ap.parse_args()

    seen, rows = set(), []
    for kw in CFG["keywords"] + a.add:
        print("検索中:", kw, file=sys.stderr)
        for r in search(kw):
            if r["id"] in seen or any(x in r["channel"] for x in CFG["exclude_channels_like"]):
                continue
            seen.add(r["id"]); rows.append(r)
    for ch in CFG["channels"]:
        print("参考チャンネル:", ch["name"], file=sys.stderr)
        for r in channel_videos(ch):
            if r["id"] not in seen:
                seen.add(r["id"]); rows.append(r)

    rows.sort(key=lambda r: -r["views"])
    is_news = lambda r: any(x in r["channel"] for x in CFG["news_channels_like"])
    people = [r for r in rows if not is_news(r)]
    news = [r for r in rows if is_news(r)]
    if a.json:
        Path(a.json).write_text(json.dumps({"people": people, "news": news}, ensure_ascii=False, indent=1), encoding="utf-8")

    def show(title, arr, n):
        print(f"\n== {title}（{len(arr)}本のうち上位{min(n, len(arr))}本）==")
        for r in arr[:n]:
            print(f"{r['views']:>10,} | {r['channel'][:14]:<14} | {r['title'][:70]} | https://youtu.be/{r['id']}")

    show("個人・解説・生き方のチャンネル", people, a.top)
    show("ニュース番組（世の中の関心の大きさの目安）", news, 15)
    print(f"\n集めた動画: {len(rows)}本（検索語 {len(CFG['keywords']) + len(a.add)}個・参考チャンネル {len(CFG['channels'])}個）", file=sys.stderr)


if __name__ == "__main__":
    main()
