"""被保護者調査（令和6年度 月次調査 確定値）の表の写しから data/nukedasenai.json を作る。
保護をやめた理由（第34表・第37表）と、一度やめてまた受け始めた世帯（第30表）、年間の保護開始世帯数（第6表）。
表の見出しの並びが想定どおりか、内訳の和が総数と合うかを確かめ、合わなければ止まる。
使い方: python3 -I scripts/extract_nukedasenai.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from xlsx_read import read_xlsx  # noqa: E402

ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")

HAISHI = ["総数", "傷病治癒", "傷病治癒（世帯主）", "傷病治癒（世帯員）", "死亡", "失そう", "働きによる収入の増加・取得",
          "働き手の転入", "社会保障給付金の増加", "仕送りの増加", "左記以外の収入の増", "親類・縁者等の引取り", "施設入所",
          "医療費の他法負担", "世帯構成の変更", "指導指示違反", "逮捕・勾留等", "累積金の増加", "その他"]
KAISHI = ["総数", "傷病による", "世帯主の傷病", "世帯員の傷病", "急迫保護で医療扶助単給", "要介護状態", "働いていた者の死亡",
          "働いていた者の離別等", "失業", "定年・自己都合", "勤務先都合（解雇等）", "老齢による収入の減少", "事業不振・倒産",
          "その他の働きによる収入の減少", "社会保障給付金の減少・喪失", "貯金等の減少・喪失", "仕送りの減少・喪失", "その他"]


def rows_of(name):
    return read_xlsx(os.path.join(DATA, name))[0][1]


def clean(v):
    return str(v).replace("\n", "").replace(" ", "").replace("　", "") if v is not None else ""


def pick(rows, labels, n):
    """左の見出しが labels（順に）の行の、数字 n 個を返す"""
    for r in rows:
        cells = [clean(c) for c in r]
        heads = [c for c in cells if c and not c.lstrip("-").isdigit()]
        if heads[:len(labels)] == labels:
            nums = [int(c) if c.isdigit() else 0 for c in cells if c.isdigit() or c in ("-", "・")]
            if len(nums) == n:
                return nums
    raise SystemExit(f"行が見つからない: {labels}")


def need(cond, msg):
    if not cond:
        raise SystemExit("合わない: " + msg)


def pct(a, b, d=1):
    return round(a / b * 100, d)


def main():
    # 第34表：世帯類型×保護廃止の理由（年度累計）
    t34 = rows_of("hihogosha_r6_t34_haishi_source.xlsx")
    need("第34表" in "".join(clean(c) for c in t34[1]), "第34表の題名")
    head = "".join(clean(c) for r in t34[3:6] for c in r)
    for h in ["傷病治癒", "死亡", "失そう", "働きによる収入の増加・取得", "累積金の増加"]:
        need(h in head, "第34表の見出し " + h)
    types = {"総数": ["年度累計", "総数"], "高齢者世帯": ["年度累計", "高齢者世帯"], "母子世帯": ["年度累計", "母子世帯"],
             "傷病者世帯": ["年度累計", "傷病者世帯"], "障害者世帯": ["年度累計", "障害者世帯"], "その他の世帯": ["年度累計", "その他の世帯"]}
    by_type = {}
    for k, lab in types.items():
        v = pick(t34, lab, len(HAISHI))
        need(v[1] == v[2] + v[3], k + " 傷病治癒の内訳")
        need(v[0] == v[1] + sum(v[4:]), k + " 理由の和と総数")
        by_type[k] = dict(zip(HAISHI, v))
    need(sum(by_type[k]["総数"] for k in types if k != "総数") == by_type["総数"]["総数"], "世帯類型の和")

    # 第37表：世帯主の年齢×保護廃止の理由（年度累計）
    t37 = rows_of("hihogosha_r6_t37_haishi_age_source.xlsx")
    need("第37表" in "".join(clean(c) for c in t37[1]), "第37表の題名")
    ages = ["19歳以下", "20～29歳", "30～39歳", "40～49歳", "50～59歳", "60～64歳", "65～69歳", "70歳以上"]
    by_age = {}
    for a in ages:
        v = pick(t37, ["年度累計", a], len(HAISHI))
        need(v[0] == v[1] + sum(v[4:]), a + " 理由の和と総数")
        by_age[a] = dict(zip(HAISHI, v))
    need(sum(by_age[a]["総数"] for a in ages) == by_type["総数"]["総数"], "年齢の和と第34表の総数")

    # 第30表：保護歴有保護開始世帯数，前回廃止時からの期間×開始の理由（年度累計）
    t30 = rows_of("hihogosha_r6_t30_saijukyu_source.xlsx")
    need("第30表" in "".join(clean(c) for c in t30[1]), "第30表の題名")
    periods = ["総数", "３月未満", "３月～６月未満", "６月～１年未満", "１年～２年未満", "２年～３年未満", "３年～４年未満", "４年～５年未満", "５年以上"]
    again = {}
    for p in periods:
        v = pick(t30, ["年度累計", p], len(KAISHI))
        again[p] = dict(zip(KAISHI, v))
    need(sum(again[p]["総数"] for p in periods[1:]) == again["総数"]["総数"], "期間の和と総数")

    # 第6表：年間の保護開始世帯数（年度累計）
    n6 = rows_of("hihogosha_n6_kaishi_source.xlsx")
    kaishi = None
    for r in n6:
        cells = [clean(c) for c in r]
        if cells and cells[0].startswith("2024年度"):
            nums = [int(c) for c in cells if c.isdigit()]
            kaishi = {"申請件数": nums[5], "保護開始世帯数": nums[6], "保護廃止世帯数": nums[8]}
    need(kaishi and kaishi["保護開始世帯数"] == 228542, "第6表 令和6年度の保護開始世帯数")

    tot = by_type["総数"]
    dead_old = by_age["65～69歳"]["死亡"] + by_age["70歳以上"]["死亡"]
    within1 = sum(again[p]["総数"] for p in ["３月未満", "３月～６月未満", "６月～１年未満"])
    out = {
        "note": "被保護者調査（令和6年度 月次調査 確定値・2026年3月4日公表）の表の写しから scripts/extract_nukedasenai.py が作ったもの。年度累計（令和6年4月〜令和7年3月）。廃止は、転出による廃止と一時的な扶助だけの世帯を除く（第34表・第37表の注）。保護歴有の開始は、転入と一時的な扶助だけの世帯を除く（第30表の注）",
        "source": {
            "kakutei": "https://www.mhlw.go.jp/toukei/saikin/hw/hihogosya/m2025/kakutei.html",
            "estat": "https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00450312&tstat=000001218960",
            "t34": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040417828&fileKind=0",
            "t37": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040417833&fileKind=0",
            "t30": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040417822&fileKind=0",
            "n6": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040417861&fileKind=0"
        },
        "haishi_by_type": by_type,
        "haishi_by_age": by_age,
        "saijukyu_by_period": again,
        "n6_r6": kaishi,
        "calc": {
            "haishi_total": tot["総数"],
            "dead": tot["死亡"], "dead_pct": pct(tot["死亡"], tot["総数"]),
            "work": tot["働きによる収入の増加・取得"], "work_pct": pct(tot["働きによる収入の増加・取得"], tot["総数"]),
            "cure": tot["傷病治癒"], "cure_pct": pct(tot["傷病治癒"], tot["総数"]),
            "dead_65plus_pct": pct(dead_old, tot["死亡"]),
            "dead_70plus_pct": pct(by_age["70歳以上"]["死亡"], tot["死亡"]),
            "work_pct_by_age": {a: pct(by_age[a]["働きによる収入の増加・取得"], by_age[a]["総数"]) for a in ages},
            "sonota_work_pct": pct(by_type["その他の世帯"]["働きによる収入の増加・取得"], by_type["その他の世帯"]["総数"]),
            "again_total": again["総数"]["総数"],
            "again_within1y": within1, "again_within1y_pct": pct(within1, again["総数"]["総数"]),
            "again_under3m": again["３月未満"]["総数"], "again_under3m_pct": pct(again["３月未満"]["総数"], again["総数"]["総数"]),
            "again_share_of_kaishi_pct": pct(again["総数"]["総数"], kaishi["保護開始世帯数"]),
            "again_reason_chokin_pct": pct(again["総数"]["貯金等の減少・喪失"], again["総数"]["総数"]),
            "again_reason_shobyo_pct": pct(again["総数"]["傷病による"], again["総数"]["総数"]),
            "again_reason_shitsugyo_pct": pct(again["総数"]["失業"], again["総数"]["総数"])
        }
    }
    with open(os.path.join(DATA, "nukedasenai.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(json.dumps(out["calc"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
