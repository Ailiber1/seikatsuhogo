# 生活保護のしらべもの

YouTubeチャンネル「リベル_Liber」の生活保護配信で使う、解説ページと調べものツールを集めたところ。

**公開URL: https://ailiber1.github.io/seikatsuhogo/**

生活保護に関して作ったものは、資料もツールも元データも生成スクリプトも、すべてこのリポジトリで管理する。
バラバラに散らさない。ローカルのフォルダには残さない。

---

## 中身

| ファイル | 種類 | 内容 | 公開URL |
|---|---|---|---|
| `index.html` | 一覧 | 視聴者に伝える1つのリンク。カードの格子・種類タブ・検索つき | [/](https://ailiber1.github.io/seikatsuhogo/) |
| `hub-items.js` | 一覧 | 一覧に並ぶカードのデータ。足すときはここに1行 | — |
| `sodan.html` | ツール | 生活の相談窓口をさがす（全国1,370か所） | [/sodan.html](https://ailiber1.github.io/seikatsuhogo/sodan.html) |
| `tokurei.html` | ツール | 特例加算しらべ（自分がいくら増えるか） | [/tokurei.html](https://ailiber1.github.io/seikatsuhogo/tokurei.html) |
| `fuyo.html` | 解説 | 生活保護を申請すると家族に通知は行くのか（扶養照会） | [/fuyo.html](https://ailiber1.github.io/seikatsuhogo/fuyo.html) |
| `basic-income.html` | 解説 | ベーシックインカムは、世界でどうなっているのか（世界の実験・制度化・日本・AIとの関係） | [/basic-income.html](https://ailiber1.github.io/seikatsuhogo/basic-income.html) |
| `tsuika.html` | ツール | 追加給付しらべ（最高裁判決の追加給付で、対象か・申し出が必要か・申し出先） | [/tsuika.html](https://ailiber1.github.io/seikatsuhogo/tsuika.html) |
| `tsuika-setsumei.html` | 解説 | 保護費の追加給付、期限までに申し出ないと0円（最高裁判決・金額の例・申し出のしかた） | [/tsuika-setsumei.html](https://ailiber1.github.io/seikatsuhogo/tsuika-setsumei.html) |
| `tokurei-setsumei.html` | 解説 | 生活保護費が10月から上がる。上がらない人もいる理由 | [/tokurei-setsumei.html](https://ailiber1.github.io/seikatsuhogo/tokurei-setsumei.html) |
| `hogohi.html` | ツール | 保護費しらべ（市区町村・人数・年齢から、保護費が毎月いくらか。生活扶助＋住宅扶助の上限） | [/hogohi.html](https://ailiber1.github.io/seikatsuhogo/hogohi.html) |
| `kyuryo.html` | ツール | 給料いくら残るしらべ（働いた給料・臨時収入のうち、手元に残る額と保護費から差し引かれる額） | [/kyuryo.html](https://ailiber1.github.io/seikatsuhogo/kyuryo.html) |
| `data/` | データ | ページに埋め込む元データ（JSON） | — |
| `scripts/` | スクリプト | 公的資料からデータを作り、ページを生成する | — |

## data/ の中身

| ファイル | 内容 | 出典 |
|---|---|---|
| `madoguchi.json` | 全国の自立相談支援機関 1,370か所（窓口名・住所・電話・メール） | 厚労省が案内する「令和7年度 自立相談支援機関窓口情報」 |
| `kyuchi_by_city.json` | 全1,741市区町村の級地区分 | 厚労省「お住まいの地域の級地を確認」＋総務省「全国地方公共団体コード」 |
| `keika.json` | 生活扶助本体に係る経過的加算（世帯人数×年齢×級地） | 厚労省「生活扶助基準額の算出方法（令和8年4月）」別表(1) |
| `ages.json` | 経過的加算の年齢区分 | 同上 |
| `jutaku_limit.json` | 住宅扶助（家賃）の上限。都道府県×1〜3級地と指定都市・中核市、1人〜7人以上。公式資料との照合結果も入れてある | 平成27年4月14日 社援発0414第9号の別表（写し `jutaku_limit_2015_source.pdf`）。厚労省・埼玉県・札幌市の公式の数字と照合 |
| `kiso_kojo.json` | 勤労収入の基礎控除額表（1人目・2人目以降）、新規就労控除・20歳未満控除・臨時収入の扱い | 厚労省「生活保護法による保護の実施要領について」（次官通知）別表（法令等データベースの画像から書き写し） |
| `kijun_r8.json` | 生活扶助の第1類・第2類・逓減率・特例加算と、照合用のモデル世帯9類型 | 厚労省「生活扶助基準額の算出方法（令和8年4月）」＋第55回生活保護基準部会 資料4 |

## scripts/ の中身

| ファイル | 役割 |
|---|---|
| `fetch_madoguchi.py` | 相談窓口の一覧を取得して `data/madoguchi.json` を作る |
| `gen_madoguchi_tool.py` | `data/madoguchi.json` から `sodan.html` を生成する |
| `gen_tsuika_tool.py` | `data/kyuchi_by_city.json` を `tsuika.template.html` に埋め込んで `tsuika.html` を生成する |
| `report_counts.py` | GoatCounter から、ページごとの開かれた回数とツールごとの結果が出た回数を取り出す（鍵はキーチェーンから読む） |
| `count_snippet.py` | 利用回数の計測（GoatCounter・SRI付き）を全ページに入れる。生成スクリプトからも使う |
| `gen_kyuryo_tool.py` | `data/kiso_kojo.json` を `kyuryo.template.html` に埋め込んで `kyuryo.html` を生成する |
| `verify_kyuryo.py` | `kyuryo.html` の計算式を node で動かし、基礎控除額表の全区分・表の外の決まり・計算例と一致するか確かめる |
| `extract_jutaku_limit.py` | 住宅扶助の上限の表をPDFから読み取り、公式の数字と照合して `data/jutaku_limit.json` を作る |
| `gen_hogohi_tool.py` | 級地・経過的加算・基準額・住宅扶助の上限を `hogohi.template.html` に埋め込んで `hogohi.html` を生成する |
| `verify_hogohi.py` | `hogohi.html` の計算式を node で動かし、資料4のモデル世帯54通りと1円単位で一致するか確かめる |

---

## 配信1回ぶんの作りかた（毎回この順番）

配信のたびに、**資料を1つ・ツールを1つ**作り、最後に**概要欄の文面**まで用意する。ここまでで1セット。

### 1. 調べる
- 過去に同じ話題を扱っていないか、チャンネルの動画を確認する（`yt-dlp --flat-playlist` で一覧、自動字幕を落として中身を確認）。**過去の発言と矛盾させない**。触れていたなら「あのとき推測で止めた部分に根拠を出す続編」として組み立てる
- 数字と条件は**公的な一次資料**（厚労省・総務省・法令）にあたる。報道は補助
- PDFは `pdftotext -layout` でテキストを取る。読めないときは高解像度で画像化して読む

### 2. 資料を1つ作る（解説ページ）
- 話の筋をそのままページの並びにする。配信では上から順にスクロールして見せる
- 中身の型は「作るときのきまり」の節を参照

### 3. ツールを1つ作る（視聴者が試せるもの）
- 「自分の場合はどうなのか」を、選ぶだけで出せるもの
- 配信では**未選択の状態から操作して実演**する。だから初期状態で結果を出さない
- 元データは `data/` に、生成スクリプトは `scripts/` に置く。**ローカルに残さない**

### 4. 概要欄の文面を用意する
リンクは**資料1つ・ツール1つだけ**。多いと押されない。

```
▼ 配信で見せた資料
（資料のタイトル）
https://ailiber1.github.io/seikatsuhogo/◯◯.html

▼ （ツールで何ができるか）
https://ailiber1.github.io/seikatsuhogo/◯◯.html
```

### 5. 一覧に追加する
`hub-items.js` の `ITEMS` に**1行**足す（`index.html` は触らない）。これで過去のものも辿れる。
- `kind` は `"tool"`（ツール）か `"doc"`（解説）、`kw` は検索用の言葉（「家賃」「バレる」など、視聴者が打ちそうなことば）
- 新しく足したものだけ `isNew:true` にし、古くなったら外す

## 作るときのきまり

### 見た目
- **常に白基調。ダークモードへの切り替えはしない。** 配信者の画面と視聴者の画面で見え方を揃えるため
- **濃い色で塗りつぶさない。** 薄い面＋左の線で表す。強い色面は怪しく見える
- 配色（そのまま使う）:
  ```
  --ground:#ffffff; --panel:#fafbfc; --ink:#242c36; --sub:#5f6a77;
  --navy:#2b5d8f; --navy-soft:#eef3f8; --on-navy:#ffffff;
  --ok:#2a7355; --ok-bg:#f1f7f4; --ng:#a4483c; --ng-bg:#fdf3f1;
  --line:#e2e7ec; --line-soft:#f0f3f6;
  ```
- 見出しは明朝、本文はゴシック。Webフォントは読み込まない（表示が遅れるため）

### 組み立て
- 冒頭に**「このページは、こういう方へ」**を置き、誰向けかを一目で分かるようにする
- そのすぐ下に**結論**を大きく出す
- 公的資料は**原文をそのまま引用**し、**元の資料へのリンク**を添える
- 仕組みの説明にはインラインSVGの図を使う（画像にしない）
- 末尾に**根拠資料の一覧**と**読むときの注意**（限界・確認日）
- いちばん最後に、**全ページ共通で**「作成：リベル_Liber（YouTubeチャンネル）」の1行を置く（リンク先はチャンネルのURL、中央寄せ・14px・太字、上に細い線）。既存ページの末尾（`hogohi.html` など）と同じ書き方にそろえる。生成スクリプトで作るページは、ひな形にも入れる

### ツール
- **開いた直後は結果を出さない。** 配信で使い方を実演するため
- ただし空の画面にはせず、「上で◯◯を選ぶと、ここに△△が出ます」という案内を出す
- プルダウンの先頭は「選んでください」。2段目は1段目が未選択のあいだ押せないようにする
- 入力内容は**ブラウザの中だけで処理し、外部に送信しない**

### 利用回数の計測（全ページ必須）
- GoatCounter（アカウント `liber-seiho`、無料・Cookieなし）で、**ページが開かれた回数**と、ツールで**結果が出た回数**だけを数える。入力した内容は送らない
- 新しいページを作ったら `python3 scripts/count_snippet.py` を実行する（全 .html に計測を入れる。入っていれば何もしない）。生成スクリプト（`gen_*.py`）は自動で入れる
- ツールは、結果を最初に出すところで `if (window.gcUse) gcUse('ツール名');` を呼ぶ（同じ画面では1回だけ数える）。GoatCounter では「利用/ツール名」として出る
- 注意書きの「どこにも送信していません」の後に「ページが開かれた回数と結果が出た回数だけは、Cookieを使わず、個人を特定しない方法で数えています。」を入れる
- 自分の利用を数えないようにするには、使うブラウザごとに一度だけ https://ailiber1.github.io/seikatsuhogo/#toggle-goatcounter を開く
- 読み取り用の鍵はリポジトリに入れない（Mac のキーチェーン `goatcounter-liber` にだけ保存）

### 事実の扱い
- 数字と条件は**公的な一次資料**（厚労省・総務省・法令）にあたる
- 推論した部分は「試算」と明記し、原文にある数字と区別する
- 各ページに**確認日**を書く

---

## 更新のしかた

```
gh repo clone Ailiber1/seikatsuhogo
# 編集して
git add -A && git commit -m "…" && git push
```

GitHub Pagesに反映されるまで1分ほどかかる。

## 注意

個人が作っているもので、行政の公式ページではない。法律上の助言でもない。

## 関連

特例加算ツールの最初の公開版は `Ailiber1/tokurei-kasan` にある（2026年9月22日の配信で配布済み。URLを壊さないためそのまま残している）。以降の更新はこのリポジトリで行う。
