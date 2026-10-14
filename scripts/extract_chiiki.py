"""地域で差が出る負担のデータを公的資料から読み取り、data/chiiki.json を作る。

使い方: python3 scripts/extract_chiiki.py <環境省の表を置いたフォルダ>
  環境省の表は47ファイル・66MBあるのでリポジトリに入れない。次のURLから 01〜47 を落として
  <フォルダ>/01_02.xlsx 〜 47_02.xlsx として置く。
  https://www.env.go.jp/recycle/waste_tech/ippan/r5/data/shori/city/NN/02.xlsx

読むもの（写しは data/ にある）
1. 物価: 総務省「消費者物価地域差指数 2025年結果」別表1（都道府県）・別表2（都市）
   data/chiikisa_2025_source.pdf  https://www.stat.go.jp/data/kouri/kouzou/pdf/g_2025.pdf
2. 光熱費・ガソリンなど: 総務省 家計調査（二人以上の世帯）品目別都道府県庁所在市及び政令指定都市ランキング
   2023年〜2025年平均「食料以外」 data/kakei_rank14_2023-2025_source.xlsx
   https://www.stat.go.jp/data/kakei/zuhyou/rank14.xlsx
3. 冬季加算: 生活保護法による保護の基準（昭和38年厚生省告示第158号）別表第1 第1章1(2)・イ
   令和8年6月11日厚生労働省告示第245号による改正（令和8年10月1日適用）時点
   https://www.mhlw.go.jp/web/t_doc?dataId=82051000&dataType=0
4. ごみの手数料: 環境省 一般廃棄物処理実態調査 令和5年度 市町村集計結果（ごみ処理体制）
   シート「手数料（生活系）」の可燃ごみ、シート「指定収集袋の導入状況」
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from xlsx_read import read_xlsx

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
PREFS = ["北海道", "青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県", "茨城県", "栃木県", "群馬県",
         "埼玉県", "千葉県", "東京都", "神奈川県", "新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県",
         "岐阜県", "静岡県", "愛知県", "三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県",
         "鳥取県", "島根県", "岡山県", "広島県", "山口県", "徳島県", "香川県", "愛媛県", "高知県", "福岡県",
         "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]

# 家計調査・地域差指数の「都市」（都道府県庁所在市＋政令指定都市5市）と、その都道府県
CITY_PREF = {
    "札幌市": "北海道", "青森市": "青森県", "盛岡市": "岩手県", "仙台市": "宮城県", "秋田市": "秋田県",
    "山形市": "山形県", "福島市": "福島県", "水戸市": "茨城県", "宇都宮市": "栃木県", "前橋市": "群馬県",
    "さいたま市": "埼玉県", "千葉市": "千葉県", "東京都区部": "東京都", "横浜市": "神奈川県", "新潟市": "新潟県",
    "富山市": "富山県", "金沢市": "石川県", "福井市": "福井県", "甲府市": "山梨県", "長野市": "長野県",
    "岐阜市": "岐阜県", "静岡市": "静岡県", "名古屋市": "愛知県", "津市": "三重県", "大津市": "滋賀県",
    "京都市": "京都府", "大阪市": "大阪府", "神戸市": "兵庫県", "奈良市": "奈良県", "和歌山市": "和歌山県",
    "鳥取市": "鳥取県", "松江市": "島根県", "岡山市": "岡山県", "広島市": "広島県", "山口市": "山口県",
    "徳島市": "徳島県", "高松市": "香川県", "松山市": "愛媛県", "高知市": "高知県", "福岡市": "福岡県",
    "佐賀市": "佐賀県", "長崎市": "長崎県", "熊本市": "熊本県", "大分市": "大分県", "宮崎市": "宮崎県",
    "鹿児島市": "鹿児島県", "那覇市": "沖縄県", "川崎市": "神奈川県", "相模原市": "神奈川県",
    "浜松市": "静岡県", "堺市": "大阪府", "北九州市": "福岡県",
}

# 冬季加算（居宅・月額）。級地によらず、地区と世帯人員で決まる（告示の1級地-1〜3級地-2の表がすべて同じ額）
TOUKI = {
    "months": {"1": 7, "2": 7, "3": 6, "4": 6, "5": 5, "6": 5},
    "period": {"1": "10月〜4月", "2": "10月〜4月", "3": "11月〜4月", "4": "11月〜4月", "5": "11月〜3月", "6": "11月〜3月"},
    # 1人, 2人, 3人, 4人, 5人
    "amount": {"1": [12780, 18140, 20620, 22270, 22890], "2": [9030, 12820, 14570, 15740, 16170],
               "3": [7460, 10590, 12030, 13000, 13350], "4": [6790, 9630, 10950, 11820, 12150],
               "5": [4630, 6580, 7470, 8070, 8300], "6": [2630, 3730, 4240, 4580, 4710]},
    "pref_area": {"北海道": 1, "青森県": 1, "秋田県": 1, "岩手県": 2, "山形県": 2, "新潟県": 2,
                  "宮城県": 3, "福島県": 3, "富山県": 3, "長野県": 3, "石川県": 4, "福井県": 4,
                  "栃木県": 5, "群馬県": 5, "山梨県": 5, "岐阜県": 5, "鳥取県": 5, "島根県": 5},  # 他は6（Ⅵ区）
}


def norm(name):
    return name.replace("ヶ", "ケ").replace("　", "").strip()


def read_chiikisa():
    txt = subprocess.run(["pdftotext", "-layout", str(DATA / "chiikisa_2025_source.pdf"), "-"],
                         capture_output=True, text=True, check=True).stdout
    lines = txt.splitlines()
    # 別表1（都道府県）: 総合・家賃を除く総合・食料・住居・光熱水道・家具家事用品（指数と順位が交互）
    pref = {}
    start = next(i for i, l in enumerate(lines) if "別表１" in l and "10大費目" in l)
    for l in lines[start:start + 70]:
        m = re.match(r"^(\S+?[都道府県])\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+", l)
        if m and m.group(1) in PREFS:
            pref[m.group(1)] = {"sogo": float(m.group(2)), "yachin_nozoku": float(m.group(3)),
                                "shokuryo": float(m.group(4)), "jukyo": float(m.group(5)),
                                "konetsu": float(m.group(6))}
    assert len(pref) == 47, len(pref)
    # 別表2（都市）: 1行に左右2都市。総合・家賃を除く総合・食料
    city = {}
    start = next(i for i, l in enumerate(lines) if "別表２" in l and "（都市）" in l)
    for l in lines[start:start + 60]:
        for m in re.finditer(r"(\S+?(?:市|区部))\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+\s+([\d.]+)\s+\d+", l):
            name = m.group(1)
            name = re.sub(r"^[都道府県庁所在政令指定]+", "", name) if name not in CITY_PREF else name
            if name in CITY_PREF:
                city[name] = {"sogo": float(m.group(2)), "yachin_nozoku": float(m.group(3)),
                              "shokuryo": float(m.group(4))}
    missing = set(CITY_PREF) - set(city)
    assert not missing, missing
    return pref, city


def read_kakei():
    name, rows = read_xlsx(DATA / "kakei_rank14_2023-2025_source.xlsx")[0]
    items = rows[1]
    units = rows[2]
    cols = {}
    for j in range(1, len(items), 2):
        item = items[j]
        if not item:
            continue
        unit = "量" if "数量" in str(units[j]) else "金額"
        cols[j] = (item, unit)
    want = {("電気代", "金額"): "denki", ("都市ガス", "金額"): "toshigas", ("プロパンガス", "金額"): "propane",
            ("灯油", "金額"): "toyu", ("灯油", "量"): "toyu_l", ("上下水道料", "金額"): "suido",
            ("バス代", "金額"): "bus", ("タクシー代", "金額"): "taxi", ("ガソリン", "金額"): "gasoline",
            ("ガソリン", "量"): "gasoline_l"}
    out = {}
    for r in rows[3:]:
        if not r or r[0] is None:
            continue
        for j, key in cols.items():
            if key not in want:
                continue
            c, v = r[j], r[j + 1]
            if c is None:
                continue
            c = "全国" if c == "全国" else c
            out.setdefault(c, {})[want[key]] = v
    assert set(out) == set(CITY_PREF) | {"全国"}, set(out) ^ (set(CITY_PREF) | {"全国"})
    for c, d in out.items():
        assert len(d) == len(want), (c, d)
    return out


def read_gomi(env_dir):
    """可燃ごみの手数料（有料・無料・一部有料・収集無し）と、指定袋を有料化として入れているか"""
    gomi = {}
    total = 0
    for i, p in enumerate(PREFS, 1):
        sheets = dict(read_xlsx(Path(env_dir) / f"{i:02d}_02.xlsx"))
        fee = sheets["手数料（生活系）"]
        # 列: 可燃ごみの手数料 14=有料 15=無料 16=一部有料 17=収集無し（見出し行5で確かめる）
        # 可燃ごみを「収集無し」と答え、混合ごみ（燃やすごみ等をまとめて集める）で答えている市がある（京都市・大阪市など）。
        # そのときは混合ごみの列 3=有料 4=無料 5=一部有料 6=収集無し を使う
        hdr = fee[5]
        assert [hdr[14], hdr[15], hdr[16], hdr[17]] == ["有料", "無料", "一部有料", "収集無し"], hdr[14:18]
        assert [hdr[3], hdr[4], hdr[5], hdr[6]] == ["有料", "無料", "一部有料", "収集無し"], hdr[3:7]
        assert fee[1][14] == "可燃ごみ" and fee[1][3] == "混合ごみ", (fee[1][3], fee[1][14])
        bag = sheets["指定収集袋の導入状況"]
        assert bag[5][7] == "有料化である" and bag[5][8] == "有料化ではない", bag[5][7:9]
        assert bag[5][3] == "導入している" and bag[5][4] == "導入していない" and bag[3][3] == "生活系ごみ", (bag[3][3], bag[5][3:5])
        bag_map, intro_map = {}, {}
        for r in bag[7:]:
            if len(r) > 2 and r[0] == p and r[2]:
                bag_map[norm(r[2])] = "有料化" if len(r) > 7 and r[7] == "○" else ("有料化ではない" if len(r) > 8 and r[8] == "○" else "")
                # 生活系ごみの収集に指定袋を入れているか（3=導入している 4=導入していない）
                intro_map[norm(r[2])] = True if len(r) > 3 and r[3] == "○" else (False if len(r) > 4 and r[4] == "○" else None)
        d = {}
        for r in fee[7:]:
            if len(r) <= 2 or r[0] != p or not r[2] or r[2] in ("合計", "東京都23区"):  # 23区はまとめ行（中身は区ごと）
                continue
            marks = [k for k, col in (("有料", 14), ("無料", 15), ("一部有料", 16), ("収集無し", 17)) if len(r) > col and r[col] == "○"]
            assert len(marks) == 1, (p, r[2], marks)
            mixed = [k for k, col in (("有料", 3), ("無料", 4), ("一部有料", 5), ("収集無し", 6)) if len(r) > col and r[col] == "○"]
            assert len(mixed) == 1, (p, r[2], mixed)
            # 燃やすごみの扱い: 可燃ごみの答え。可燃ごみが収集無しなら混合ごみの答え
            moyasu = mixed[0] if marks[0] == "収集無し" else marks[0]
            d[norm(r[2])] = {"kanen": marks[0], "kongo": mixed[0], "moyasu": moyasu, "bag": bag_map.get(norm(r[2]), ""), "shitei": intro_map.get(norm(r[2]))}
        # 合計行の数と一致するか
        tot = fee[6]
        assert tot[2] == "合計"
        cnt = {k: sum(1 for v in d.values() if v["kanen"] == k) for k in ("有料", "無料", "一部有料", "収集無し")}
        assert [cnt["有料"], cnt["無料"], cnt["一部有料"], cnt["収集無し"]] == [tot[14], tot[15], tot[16], tot[17]], (p, cnt, tot[14:18])
        gomi[p] = d
        total += len(d)
    return gomi, total


def main():
    env_dir = sys.argv[1]
    pref_idx, city_idx = read_chiikisa()
    kakei = read_kakei()
    gomi, n_gomi = read_gomi(env_dir)

    # 級地データ（全1,741市区町村）と、ごみの表の市区町村名を突き合わせる
    kyuchi = json.loads((DATA / "kyuchi_by_city.json").read_text(encoding="utf-8"))["data"]
    unmatched = []
    for p, cities in kyuchi.items():
        for name, _ in cities:
            if norm(name) not in gomi[p]:
                unmatched.append((p, name))
    extra = [(p, n) for p in gomi for n in gomi[p] if n not in {norm(c) for c, _ in kyuchi[p]}]

    out = {
        "note": "地域で差が出る負担。scripts/extract_chiiki.py が公的資料から作る。出典はスクリプトの説明を参照。",
        "checked": "2026-10-15",
        "touki": TOUKI,
        "price_pref": pref_idx,
        "price_city": city_idx,
        "city_pref": CITY_PREF,
        "kakei": kakei,
        "gomi": gomi,
    }
    (DATA / "chiiki.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("物価（都道府県）", len(pref_idx), "／物価（都市）", len(city_idx), "／家計調査の都市", len(kakei) - 1)
    print("ごみの表の市区町村", n_gomi, "／級地の表にあってごみの表に無い", unmatched, "／逆", extra)


if __name__ == "__main__":
    main()
