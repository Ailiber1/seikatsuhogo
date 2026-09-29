"""GoatCounter から、ページごとの「開かれた回数」とツールごとの「結果が出た回数」を取り出して表にする。

鍵はリポジトリに置かず、Mac のキーチェーン（サービス名 goatcounter-liber）から読む。
使い方: python3 scripts/report_counts.py [開始日 YYYY-MM-DD] [終了日 YYYY-MM-DD]
        （省略すると、2026-09-29 から今日まで）
"""
import datetime as dt, getpass, json, subprocess, sys, urllib.parse, urllib.request

SITE = "https://liber-seiho.goatcounter.com"
start = sys.argv[1] if len(sys.argv) > 1 else "2026-09-29"
end = sys.argv[2] if len(sys.argv) > 2 else dt.date.today().isoformat()
key = subprocess.run(["security", "find-generic-password", "-a", getpass.getuser(), "-s", "goatcounter-liber", "-w"],
                     capture_output=True, text=True, check=True).stdout.strip()


def get(path, **q):
    url = f"{SITE}/api/v0/{path}?" + urllib.parse.urlencode(q)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


# 終了日はその日の終わりまで含める
end_excl = (dt.date.fromisoformat(end) + dt.timedelta(days=1)).isoformat()
rows, after = [], None
while True:
    q = {"start": f"{start}T00:00:00Z", "end": f"{end_excl}T00:00:00Z", "limit": 100}
    if after:
        q["exclude_paths"] = after
    d = get("stats/hits", **q)
    rows += d.get("hits", [])
    if not d.get("more"):
        break
    after = ",".join(str(h["path_id"]) for h in rows)

views = sorted([h for h in rows if not h.get("event")], key=lambda h: -h["count"])
uses = sorted([h for h in rows if h.get("event")], key=lambda h: -h["count"])
print(f"期間: {start} 〜 {end}（日本時間ではなく世界標準時で区切り）")
print("\n■ ページが開かれた回数")
for h in views:
    print(f"{h['count']:>6}  {h['path']}")
print("\n■ ツールで結果が出た回数")
for h in uses:
    print(f"{h['count']:>6}  {h['path']}")
