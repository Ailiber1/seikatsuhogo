"""総務省「令和3年社会生活基本調査」第7-1表から、1日の生活時間の平均を取り出して data/jikan_r3.json を作る。

元の表: 曜日,男女,配偶関係,ふだんの就業状態,年齢,行動の種類別総平均時間(15歳以上)－全国
  https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032223892&fileKind=0
  （写し: data/shakai2021_t7-1_source.xlsx）

20種類の行動を、ツールの6項目にまとめる（合計はどの行も1440分＝24時間になる）。
  睡眠       … 01睡眠
  仕事・学校 … 04通勤・通学 05仕事 06学業
  家事       … 07家事 08介護・看護 09育児 10買い物
  食事・身支度 … 02身の回りの用事 03食事
  自由な時間 … 12テレビ・ラジオ・新聞・雑誌 13休養・くつろぎ 14学習・自己啓発・訓練
               15趣味・娯楽 16スポーツ 17ボランティア活動 18交際・付き合い
  その他     … 11移動 19受診・療養 20その他

使い方: python3 scripts/extract_jikan.py
"""
import html
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "shakai2021_t7-1_source.xlsx"
OUT = ROOT / "data" / "jikan_r3.json"

GROUPS = {
    "sleep": ["01"],
    "work": ["04", "05", "06"],
    "house": ["07", "08", "09", "10"],
    "meal": ["02", "03"],
    "free": ["12", "13", "14", "15", "16", "17", "18"],
    "other": ["11", "19", "20"],
}
DAYS = {"1": "week", "2": "weekday", "3": "sat", "4": "sun"}
SEX = {"0": "all", "1": "m", "2": "f"}
WORK = {"0": "all", "1": "yes", "2": "no"}


def read_rows(path):
    z = zipfile.ZipFile(path)
    ss = []
    x = z.read("xl/sharedStrings.xml").decode()
    for si in re.findall(r"<si>(.*?)</si>", x, re.S):
        ss.append(html.unescape("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))))
    x = z.read("xl/worksheets/sheet1.xml").decode()
    rows = []
    for r in re.findall(r"<row[^>]*>(.*?)</row>", x, re.S):
        cells = {}
        for c in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', r, re.S):
            col, attr, inner = c.groups()
            v = re.search(r"<v>(.*?)</v>", inner or "")
            if not v:
                cells[col] = ""
                continue
            val = v.group(1)
            cells[col] = ss[int(val)] if 't="s"' in attr else val
        rows.append(cells)
    return rows


def main():
    rows = read_rows(SRC)
    # 見出し行から「行動コード → 列」を作る
    head = next(r for r in rows if r.get("G", "").startswith("01_"))
    code_col = {v.split("_")[0]: k for k, v in head.items() if re.match(r"^\d\d_", v)}
    n_col = next(k for k, v in rows[2].items() if v == "サンプルサイズ")

    out = {}
    for r in rows:
        a, b, c, d, e = (r.get(k, "") for k in "ABCDE")
        if not (a[:1] in DAYS and "_" in a and c.startswith("0_") and "_" in e):
            continue
        age = e.split("_")[0]
        if not re.fullmatch(r"\d\d", age):  # 再掲(R1〜)は使わない
            continue
        key = "|".join([DAYS[a[0]], SEX[b[0]], WORK[d[0]], age])
        mins = {}
        ok = True
        for g, codes in GROUPS.items():
            s = 0
            for code in codes:
                v = r.get(code_col[code], "")
                s += 0 if v in ("-", "") else int(v)
            mins[g] = s
        total = sum(mins.values())
        # 表の数字は分単位の丸めなので、合計が1440から数分ずれることがある
        if abs(total - 1440) > 5:
            ok = False
        out[key] = {**mins, "n": int(r.get(n_col) or 0), "total": total, "ok": ok}

    ages = {}
    for r in rows:
        e = r.get("E", "")
        if re.fullmatch(r"\d\d_.+", e):
            ages[e.split("_")[0]] = e.split("_", 1)[1]
    doc = {
        "source": "総務省「令和3年社会生活基本調査」生活時間 第7-1表（15歳以上・全国）",
        "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000032223892&fileKind=0",
        "groups": GROUPS,
        "ages": ages,
        "data": out,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    bad = [k for k, v in out.items() if not v["ok"]]
    print(f"{len(out)}区分を書き出しました。合計が24時間から5分以上ずれた区分: {bad or 'なし'}")


if __name__ == "__main__":
    main()
