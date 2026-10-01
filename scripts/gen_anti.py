"""アンチコメ図鑑（anti.html）と、アンチコメ返し（anti-kaeshi.html）を生成する。

- 元データは data/anti.json。投稿者名・チャンネル名は入っていない（本文だけ）
- 件数・順位・割合は、すべてこのスクリプトが data/anti.json から数える。ページに手で数字を書かない
- 数が合わないとき（合計と内訳がずれる等）は、ページを作らずに止まる

使い方: python3 scripts/gen_anti.py
"""
import json
from collections import Counter
from pathlib import Path

from count_snippet import add_snippet

ROOT = Path(__file__).resolve().parent.parent
D = json.loads((ROOT / "data" / "anti.json").read_text(encoding="utf-8"))

SEIHO = "https://www.mhlw.go.jp/web/t_doc?dataId=82048000&dataType=0&pageNo=1"
HOSOKU = "https://www.mhlw.go.jp/shingi/2004/01/s0127-7k.html"
TOBEN = "https://www.shugiin.go.jp/internet/itdb_shitsumon.nsf/html/shitsumon/b183001.htm"
TOKYO = "https://www.soumu.metro.tokyo.lg.jp/documents/d/soumu/0292_146"

# 種類ごとの「ひとこと」と、事実での答え。引用は元の資料の原文のまま
ANSWERS = {
    "W": {
        "nick": "とにかく働かせたい人たち",
        "answer": "働けるかどうかを決めるのは、コメント欄ではなく福祉事務所です。国は「能力があるか」「働く意思があるか」「実際に働く場があるか」の3つで判断するとしています。",
        "quotes": [
            {"text": "稼働能力を活用しているか否かについては、(1)稼働能力を有するか否か (2)その稼働能力を活用する意思があるか否か (3)実際に稼働能力を活用する就労の場を得ることができるか否か の３つの要素により判断",
             "src": "厚生労働省 社会保障審議会 生活保護制度の在り方に関する専門委員会 資料「補足性の原理について」", "url": HOSOKU},
        ],
        "self": "ちなみに私は、YouTubeと在宅ワークで収入のある仕事を1日7時間30分しています。", "selflink": ["hima-setsumei.html", "生活保護は暇じゃない"],
    },
    "T": {
        "nick": "納税者代表の人たち",
        "answer": "保護費が税金から出ているのは、そのとおりです。ただ、それは法律が決めた税金の使い道です。国が4分の3を負担すること、要件を満たせば誰でも受けられることが、法律に書いてあります。",
        "quotes": [
            {"text": "すべて国民は、この法律の定める要件を満たす限り、この法律による保護を、無差別平等に受けることができる。", "src": "生活保護法 第2条", "url": SEIHO},
            {"text": "国は、政令で定めるところにより、次に掲げる費用を負担しなければならない。一　市町村及び都道府県が支弁した保護費、保護施設事務費及び委託事務費の四分の三", "src": "生活保護法 第75条", "url": SEIHO},
        ],
    },
    "L": {
        "nick": "部屋と持ち物を見張る人たち",
        "answer": "パソコンやスマホのような生活用品は、その地域で7割を超える世帯が持っているものなら、原則として持っていてよいことになっています。部屋がきれいなのは、掃除をしているからです。",
        "quotes": [
            {"text": "それ以外の生活用品については、当該地域の普及率が70％を超えるものについては、地域住民との均衡などを勘案の上、原則として保有を容認",
             "src": "厚生労働省 社会保障審議会 生活保護制度の在り方に関する専門委員会 資料「補足性の原理について」", "url": HOSOKU},
        ],
    },
    "D": {
        "nick": "画面ごしに診断する人たち",
        "answer": "病気かどうか、働けるかどうかは、動画の見た目では分かりません。判断するのは福祉事務所で、国が示している判断の要素も決まっています。",
        "quotes": [
            {"text": "稼働能力を活用しているか否かについては、(1)稼働能力を有するか否か (2)その稼働能力を活用する意思があるか否か (3)実際に稼働能力を活用する就労の場を得ることができるか否か の３つの要素により判断",
             "src": "厚生労働省 社会保障審議会 生活保護制度の在り方に関する専門委員会 資料「補足性の原理について」", "url": HOSOKU},
        ],
    },
    "F": {
        "nick": "コメント欄のケースワーカーたち",
        "answer": "収入があったら届け出る。これが法律の決まりです。届け出たうえで得た収入は、不正受給ではありません。なお、不正受給の金額は、政府の答弁では保護費全体の約0.39%（平成22年度）です。",
        "quotes": [
            {"text": "被保護者は、収入、支出その他生計の状況について変動があつたとき、又は居住地若しくは世帯の構成に異動があつたときは、すみやかに、保護の実施機関又は福祉事務所長にその旨を届け出なければならない。", "src": "生活保護法 第61条", "url": SEIHO},
            {"text": "平成二十二年度における生活保護費の総額に対する不正受給の金額の割合は、約〇・三九パーセントである。", "src": "衆議院 内閣衆質183第1号 答弁書（平成25年2月5日）", "url": TOBEN},
        ],
    },
    "S": {
        "nick": "貯金を許さない人たち",
        "answer": "保護費をやり繰りして貯めたお金は、使い道が生活保護の趣旨に反しなければ、持っていてよいことになっています。たとえば家電の買い替えに備える、といった目的です。認められるかどうかは、福祉事務所が使い道を聞いて判断します。",
        "quotes": [
            {"text": "当該預貯金等の使用目的を聴取し、その使用目的が生活保護の趣旨目的に反しないと認められる場合については、活用すべき資産には当たらないものとして、保有を容認して差しつかえない。",
             "src": "厚生省社会局保護課長通知 第3・問18・答（東京都行政不服審査会の答申書に引用されたもの）", "url": TOKYO},
        ],
    },
    "N": {
        "nick": "頼んでいない家計アドバイザーたち",
        "answer": "節約に努めることは、法律で本人の務めとされています。ただ、パックご飯にするか炊くか、水をどう買うかまで決めるのは本人です。決められた保護費の中でやり繰りしています。",
        "quotes": [
            {"text": "被保護者は、常に、能力に応じて勤労に励み、自ら、健康の保持及び増進に努め、収入、支出その他生計の状況を適切に把握するとともに支出の節約を図り、その他生活の維持及び向上に努めなければならない。", "src": "生活保護法 第60条", "url": SEIHO},
        ],
    },
    "P": {
        "nick": "チャンネルの将来を心配する人たち",
        "answer": "生活保護を受けている人が発信することを禁じる決まりは、今回調べた法律と通知の中には見当たりませんでした。収入が出たら届け出る、という決まりがあるだけです。",
        "quotes": [
            {"text": "被保護者は、収入、支出その他生計の状況について変動があつたとき、又は居住地若しくは世帯の構成に異動があつたときは、すみやかに、保護の実施機関又は福祉事務所長にその旨を届け出なければならない。", "src": "生活保護法 第61条", "url": SEIHO},
        ],
    },
    "M": {
        "nick": "苦労くらべをする人たち",
        "answer": "生活が苦しいなら、あなたも申請できます。要件を満たせば、誰でも同じように受けられる制度です。",
        "quotes": [
            {"text": "すべて国民は、この法律の定める要件を満たす限り、この法律による保護を、無差別平等に受けることができる。", "src": "生活保護法 第2条", "url": SEIHO},
        ],
    },
    "H": {
        "nick": "髪型が気になる人たち",
        "answer": "髪の毛と体型は、生活保護の制度と関係がありません。返せる資料がないので、そのまま受け取ります。",
        "quotes": [],
    },
    "A": {
        "nick": "ただ言いたいだけの人たち",
        "answer": "中身が悪口だけなので、返せる事実がありません。AIが読んで、静かにブロックしています。",
        "quotes": [],
    },
}


def build():
    names, order = D["names"], D["order"]
    items = D["mine"]["items"]
    cnt = Counter(i["cat"] for i in items)

    # ここから下は、数が合っているかの確かめ。1つでも外れたら止まる
    assert set(cnt) == set(order) == set(names) == set(ANSWERS), "種類の一覧がそろっていない"
    assert sum(cnt.values()) == D["mine"]["anti"] == len(items), "自分の件数の合計が合わない"
    assert D["mine"]["anti_visible"] + D["mine"]["anti_moderator_only"] == D["mine"]["anti"], "内訳が合わない"
    assert len({i["text"] for i in items}) == len(items), "同じコメントが2回入っている"
    o = D["others"]
    assert sum(c["read"] for c in o["channels"]) == o["read"], "他チャンネルの読んだ件数が合わない"
    assert sum(c["anti"] for c in o["channels"]) == o["anti"] == sum(o["cats"].values()), "他チャンネルのアンチ件数が合わない"
    assert all("@" not in i["text"] for i in items), "投稿者名らしきものが本文に残っている"

    ranked = sorted(order, key=lambda c: (-cnt[c], order.index(c)))
    cats = []
    rank = 0
    for k, c in enumerate(ranked):
        if k == 0 or cnt[c] != cnt[ranked[k - 1]]:
            rank = k + 1  # 同じ件数は同じ順位
        cats.append({
            "id": c, "name": names[c], "rank": rank, "n": cnt[c],
            "others": o["cats"].get(c, 0),
            "texts": [i["text"] for i in items if i["cat"] == c],
            "mod": [i["text"] for i in items if i["cat"] == c and i["src"] == "moderator"],
            "examples": o["examples"].get(c, []),
            **ANSWERS[c],
        })
    data = {
        "checked": D["checked"],
        "mine": {k: D["mine"][k] for k in ("videos", "read", "anti", "anti_visible", "anti_moderator_only")},
        "others": {"read": o["read"], "anti": o["anti"], "channels": o["channels"]},
        "cats": cats,
    }
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    for tpl, out in (("anti.template.html", "anti.html"), ("anti-kaeshi.template.html", "anti-kaeshi.html")):
        html = (ROOT / "scripts" / tpl).read_text(encoding="utf-8")
        assert "__DATA__" in html, tpl
        (ROOT / out).write_text(add_snippet(html.replace("__DATA__", js)), encoding="utf-8")
        print("作成:", out)
    print("自分: 読んだ %d件 / アンチ %d件" % (data["mine"]["read"], data["mine"]["anti"]))
    print("他: 読んだ %d件 / アンチ %d件" % (o["read"], o["anti"]))
    for c in cats:
        print("  %2d位 %3d件 %s" % (c["rank"], c["n"], c["name"]))


if __name__ == "__main__":
    build()
