"""住宅扶助（家賃・間代等）の限度額の表を data/jutaku_limit.json にする。

元資料: 平成27年4月14日 社援発0414第9号「生活保護法による保護の基準に基づき厚生労働大臣が別に定める
住宅扶助（家賃・間代等）の限度額の設定について」の別表（1（1）世帯人員別の限度額）。
厚労省サイトに通知本体が見当たらないため、写し（data/jutaku_limit_2015_source.pdf）から読み取り、
公式の数字（厚労省・自治体のページ）との照合結果を data/jutaku_limit.json の check に残す。

使い方: python3 scripts/extract_jutaku_limit.py
"""
import json, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
txt = subprocess.run(["pdftotext", "-layout", str(ROOT / "data" / "jutaku_limit_2015_source.pdf"), "-"],
                     capture_output=True, text=True, check=True).stdout
sec = txt[:txt.index("１（２）")]
yen = r"([\d,]+)円"
pref, city = {}, {}
for line in sec.splitlines():
    m = re.match(r"^\s*(\S+?[都道府県])\s+([１２３123])級地\s+" + r"\s+".join([yen] * 5) + r"\s*$", line)
    if m:
        pref.setdefault(m.group(1), {})[str("１２３123".index(m.group(2)) % 3 + 1)] = [int(v.replace(",", "")) for v in m.groups()[2:]]
        continue
    m = re.match(r"^\s*(\S+?[市])\s+" + r"\s+".join([yen] * 5) + r"\s*$", line)
    if m:
        city[m.group(1)] = [int(v.replace(",", "")) for v in m.groups()[1:]]

out = {
    "note": "住宅扶助（家賃・間代等）の世帯人員別の限度額。値の並びは [1人, 2人, 3〜5人, 6人, 7人以上]。pref は都道府県×級地（1・2・3級地）、city は指定都市・中核市（2015年4月時点）。出典は scripts/extract_jutaku_limit.py の説明を参照。",
    "pref": pref, "city": city,
    # 2015年4月より後に中核市になった市。市ごとの限度額が別に定められているが公式資料を確認できないため、ツールでは県の額を出し注意書きを付ける
    "later_core_cities": ["呉市", "佐世保市", "八戸市", "川口市", "八尾市", "明石市", "鳥取市", "松江市", "福島市", "山形市",
                          "福井市", "甲府市", "寝屋川市", "水戸市", "吹田市", "松本市", "一宮市"],
    "check": [
        {"source": "厚労省「生活扶助基準額の算出方法（令和8年4月）」住宅扶助の欄（東京都・単身）", "url": "https://www.mhlw.go.jp/content/001152601.pdf",
         "expect": {"東京都/1級地/1人": 53700, "東京都/2級地/1人": 45000, "東京都/3級地/1人": 40900}},
        {"source": "埼玉県「住宅扶助基準額（生活保護法）」", "url": "https://www.pref.saitama.lg.jp/a0602/seihozenpan/910-20091209-89.html",
         "expect": {"埼玉県/1級地": [47700, 57000, 62000, 67000, 74400], "埼玉県/2級地": [43000, 52000, 56000, 60000, 67000], "埼玉県/3級地": [37000, 44000, 48000, 52000, 58000]}},
        {"source": "札幌市「生活保護基準額表（令和7年10月1日現在）」", "url": "https://www.city.sapporo.jp/fukushi-guide/documents/seikatsuhogo-r7-10model.pdf",
         "expect": {"札幌市": [36000, 43000, 46000, 50000, 56000]}},
        {"source": "長崎市・単身の実際の住宅扶助（配信者の保護決定の額）", "url": "",
         "expect": {"長崎市/1人": 36000}}
    ],
}
ok = ng = 0
for c in out["check"]:
    for key, exp in c["expect"].items():
        parts = key.split("/")
        row = city[parts[0]] if parts[0] in city else pref[parts[0]][parts[1][0]]
        got = row if isinstance(exp, list) else row[0]
        if got == exp: ok += 1
        else: ng += 1; print("不一致:", key, got, exp)
print("公式の数字との照合: 一致", ok, "件 / 不一致", ng, "件")
if ng: raise SystemExit(1)
(ROOT / "data" / "jutaku_limit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("都道府県", len(pref), "／都道府県×級地", sum(len(v) for v in pref.values()), "／市", len(city))
