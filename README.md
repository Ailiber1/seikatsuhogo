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
| `related.js` | 部品 | ページの下に「あわせて読みたい」を出し、鍵付きページへの本文リンクを押せなくする。ページごとの関連は中の `RELATED` に書く。まとめサイト以外の全ページが読み込む（`count_snippet.py` が自動で入れる） | — |
| `video-embed.js` | 部品 | YouTube動画を「押したら読み込む」形で置く。全ページ共通 | — |
| `sodan.html` | ツール | 生活の相談窓口をさがす（全国1,370か所） | [/sodan.html](https://ailiber1.github.io/seikatsuhogo/sodan.html) |
| `tokurei.html` | ツール | 特例加算しらべ（自分がいくら増えるか） | [/tokurei.html](https://ailiber1.github.io/seikatsuhogo/tokurei.html) |
| `fuyo.html` | 解説 | 生活保護を申請すると家族に通知は行くのか（扶養照会） | [/fuyo.html](https://ailiber1.github.io/seikatsuhogo/fuyo.html) |
| `basic-income.html` | 解説 | ベーシックインカムは、世界でどうなっているのか（世界の実験・制度化・日本・AIとの関係） | [/basic-income.html](https://ailiber1.github.io/seikatsuhogo/basic-income.html) |
| `tsuika.html` | ツール | 追加給付しらべ（最高裁判決の追加給付で、対象か・申し出が必要か・申し出先） | [/tsuika.html](https://ailiber1.github.io/seikatsuhogo/tsuika.html) |
| `tsuika-setsumei.html` | 解説 | 保護費の追加給付、期限までに申し出ないと0円（最高裁判決・金額の例・申し出のしかた） | [/tsuika-setsumei.html](https://ailiber1.github.io/seikatsuhogo/tsuika-setsumei.html) |
| `tokurei-setsumei.html` | 解説 | 生活保護費が10月から上がる。上がらない人もいる理由 | [/tokurei-setsumei.html](https://ailiber1.github.io/seikatsuhogo/tokurei-setsumei.html) |
| `hogohi.html` | ツール | 保護費しらべ（市区町村・人数・年齢から、保護費が毎月いくらか。生活扶助＋住宅扶助の上限） | [/hogohi.html](https://ailiber1.github.io/seikatsuhogo/hogohi.html) |
| `kyuryo.html` | ツール | 給料いくら残るしらべ（働いた給料・臨時収入のうち、手元に残る額と保護費から差し引かれる額） | [/kyuryo.html](https://ailiber1.github.io/seikatsuhogo/kyuryo.html) |
| `hima.html` | ツール | 暇人スキャン（ふだんの1日を国の平均・リスナーの平均とくらべて、暇人かどうか判定）。**リスナーの結果を名前なしで保存する唯一のツール**（下の「リスナーの結果の保存」） | [/hima.html](https://ailiber1.github.io/seikatsuhogo/hima.html) |
| `hima-setsumei.html` | 解説 | 生活保護は暇じゃない。3年目の1日を国の平均とくらべた（国の定義だと収入のある仕事は7時間30分で「かなりの暇人」、ながらAI作業まで足すと作業時間は合計16時間45分） | [/hima-setsumei.html](https://ailiber1.github.io/seikatsuhogo/hima-setsumei.html) |
| `anti.html` | 解説 | アンチコメ図鑑。このチャンネルの動画185本のコメント880件を全部読み、アンチコメ151件を11種類に分けて多い順に並べた。原文（投稿者名なし）、法律と国の資料での答え、ほかの生活保護YouTuber 11チャンネルとの比較（名前は伏せる） | [/anti.html](https://ailiber1.github.io/seikatsuhogo/anti.html) |
| `anti-kaeshi.html` | ツール | アンチコメ返し（言われた言葉を選ぶと、同じ種類が何件届いたかと、事実での答え・原文の引用が出る） | [/anti-kaeshi.html](https://ailiber1.github.io/seikatsuhogo/anti-kaeshi.html) |
| `chokin.html` | ツール | 貯金の境目しらべ（申請のとき手元に残せるお金＝最低生活費の5割の目安、車・家電・保険など持ち物ごとに売る必要があるか） | [/chokin.html](https://ailiber1.github.io/seikatsuhogo/chokin.html) |
| `chokin-setsumei.html` | 解説 | 生活保護を受けられる貯金の境目は、いくら？（3年目の申請の実体験・課長通知の「5割」・家具家電は売らなくていい） | [/chokin-setsumei.html](https://ailiber1.github.io/seikatsuhogo/chokin-setsumei.html) |
| `blacklist.html` | ツール | ブラックリスト、いつ消える？しらべ（破産手続開始決定と免責確定の年月から、CIC・JICC・全国銀行個人信用情報センターで記録がいつまで残るかの目安） | [/blacklist.html](https://ailiber1.github.io/seikatsuhogo/blacklist.html) |
| `jikohasan-setsumei.html` | 解説 | 【借金に悩む人へ】自己破産は人生の終わりじゃなかった（私の申請〜終了の記録と当時の動画6本・裁判所の説明・「ブラックリスト」は5〜7年・クレジットとデビットカード・法テラス） | [/jikohasan-setsumei.html](https://ailiber1.github.io/seikatsuhogo/jikohasan-setsumei.html) |
| `shitsugyo.html` | ツール | 失業・低収入チェック（仕事を失った人は失業給付の日数・1日の額・待つ期間とその後の支え、働いている人は生活保護の基準より何円少ないか） | [/shitsugyo.html](https://ailiber1.github.io/seikatsuhogo/shitsugyo.html) |
| `shitsugyo-setsumei.html` | 解説 | 失業者180万人、次はあなたかも。仕事を失っても、生活保護を頼っていい理由（クビにならないは本当？・3段の支え・私がこぼれた話・働いていても受けられる・年収250万円との比べ） | [/shitsugyo-setsumei.html](https://ailiber1.github.io/seikatsuhogo/shitsugyo-setsumei.html) |
| `database.rules.json` / `firebase.json` / `.firebaserc` | 設定 | 暇人スキャンの保存先（Firebase Realtime Database）の書き込みルール | — |
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
| `jikan_r3.json` | 1日の生活時間の平均（曜日×男女×働いているか×5歳刻みの年齢）。20種類の行動を6項目にまとめたもの | 総務省「令和3年社会生活基本調査」第7-1表（写し `shakai2021_t7-1_source.xlsx`） |
| `anti.json` | アンチコメの本文と種類（投稿者名なし）、ほかのチャンネルの集計（チャンネル名なし・Aさん〜Kさん）。2026年10月1日に、公開コメントとAIモデレーターの記録を1件ずつ読んで分けたもの | このチャンネルと、ほかの生活保護系チャンネルのコメント欄 |
| `blacklist.json` | 3つの信用情報機関で、自己破産の記録をいつから何年持つかの決まり（原文・出典つき）と注意点 | 全国銀行個人信用情報センター「登録情報開示報告書の見方」Q5・Q6、CIC・JICCのFAQと登録期間のページ |
| `jikohasan.json` | 自己破産の解説で使った動画6本・引用した原文・出典URL・確認日、配信者本人が伝えた事実 | 千葉地裁・大分地裁（写し `jikohasan_chiba_source.pdf`・`jikohasan_oita_source.pdf`）、CIC・JICC・全国銀行個人信用情報センター、全国銀行協会、法テラス |
| `shitsugyo.json` | 失業給付（基本手当）の日数の表・受ける条件・給付制限・1日の額の計算式（令和8年8月1日から）、求職者支援制度・住居確保給付金・生活保護の原文、労働力調査・解雇・希望退職・倒産の数字 | ハローワーク（写し `hellowork_benefitdays_source.html`）、厚労省「基本手当日額の計算式及び金額」（写し `kihon_nichigaku_r8_source.pdf`）、総務省 労働力調査 2026年8月分（写し `rodo_2026_08_gaiyou_source.pdf`）、東京商工リサーチ、e-Gov |
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
| `extract_jikan.py` | 社会生活基本調査の表から `data/jikan_r3.json` を作る（全区分の合計が24時間になるか確かめる） |
| `gen_hima_tool.py` | `data/jikan_r3.json` を `hima.template.html` に埋め込んで `hima.html` を生成する |
| `gen_anti.py` | `data/anti.json` から `anti.html` と `anti-kaeshi.html` を生成する。件数・順位・割合はここで数え、合計と内訳が合わないときは止まる |
| `gen_chokin_tool.py` | 級地・経過的加算・基準額・住宅扶助の上限を `chokin.template.html` に埋め込んで `chokin.html` を生成する |
| `verify_chokin.py` | `chokin.html` の生活扶助の計算が `hogohi.html` と同じでモデル世帯54通りと一致するか、残せる額の判定の境目が正しいかを確かめる |
| `verify_blacklist.py` | `blacklist.html` の計算式を node で動かし、7年・5年の決まりどおりの年月と、同じ月に消える機関の表示・「今月ごろ」の境目が正しいか確かめる |
| `gen_shitsugyo_tool.py` | 失業給付の決まり・級地・基準額・住宅扶助の上限・基礎控除額表を `shitsugyo.template.html` に埋め込んで `shitsugyo.html` を生成する |
| `verify_shitsugyo.py` | 給付日数の表をハローワークの写しから読み直して照合し、1日の額が上限・下限と一致して途切れないか、生活扶助・基礎控除が他のツールと同じか確かめる |
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
- そのツール・解説を説明する動画をページに置いたら、そのカードに `video:true` を付ける（「▶動画あり」が出る）。まとめページに動画そのものは置かない（YouTube APIは使わない）
- 関係のない近況の動画などは入れない。**そのツール・解説を説明している動画だけ**

### ページどうしをつなぐ（内部リンク）
- 新しい資料・ツールを足したら、`related.js` の `RELATED` に「そのページ → 関連させるページ（最大4つ）」を足し、**相互に張るなら相手側にも足す**。`python3 scripts/count_snippet.py` で全ページに部品が入る
- 本文の中の内部リンク（`<a href="xxx.html">`）は**鍵付きのページにも最初から張ってよい**。`hub-items.js` で `locked:true` のあいだは、自動で「🔐 配信で公開予定のページ」になって押せない。鍵（`locked:true`）を消せば、本文のリンクも「あわせて読みたい」も自動で押せるようになる
- いま開いているページ自体が鍵付きのときは、鍵付きページどうしのリンクは押せる（配信前の確認用）
- 生成ページ（`gen_*.py`）の中で変数名 `ITEMS` は使わない（`hub-items.js` と衝突する）

### 動画をページに置く
ページの「こういう方へ」の枠の下に、次の1行を置く。ファイルの末尾に `<script src="video-embed.js" defer></script>` も1回置く。
```html
<div data-yt data-id="動画ID" data-title="動画の題名" data-label="動画でも解説しています"></div>
```
- 最初は絵（サムネイル）だけ出て、押すと `youtube-nocookie.com` で読み込む。ページを開いただけでは動画側に読み込みに行かないので、「Cookieを使わない」の説明と両立する（サムネイル画像だけは開いた時点でYouTubeの画像サーバーから取得する）
- **予約投稿中・限定公開・非公開の動画は入れない。公開されてから足す**（公開前のIDを入れると、リスナーには再生できない動画が出てしまう）
- 動画IDは、公開状態と埋め込み許可を確認してから入れる（`yt-dlp --skip-download --print "%(availability)s %(playable_in_embed)s" URL` で `public True` なら可。あるいは `curl "https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=ID&format=json"` が200なら可）

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
- **これまでの資料・ツールで関係するものは、本文の該当箇所に内部リンクで紹介する**（まとめサイトの別のページも見てもらうため）。作る前に `hub-items.js` を見て話題が重なるページを探し、相対パスで「→ 〇〇も見る」のように文の流れの中に置く。鍵付きのページは公開済みか確かめてから
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

### リスナーの結果の保存（暇人スキャンだけ・2026年9月30日にユーザーが決定）
- 「ほかのリスナーとくらべる」ために、スキャンした内容を**名前なしで**保存する。保存するのは 性別・年代・働いているか・生活保護（受けている/検討中/受けていない/答えない）・6項目の時間 と保存時刻だけ。名前・住所・都道府県・IPアドレス・端末の情報は保存しない
- 同じブラウザからは**最初の1回だけ**保存する（ブラウザの localStorage に印を残す。2回目からは判定だけ出す）。1人が何度も押して平均が偏らないようにするため（2026年9月30日ユーザー決定。1日1回だと毎日試す人が重複して数えられるので変更）
- 保存先: Firebase Realtime Database（プロジェクト `seikatsuhogo`、無料のSparkプラン・課金なし）`/jikan/r`
- ルール（`database.rules.json`）: 新しい記録の追加だけ可（書き換え・削除は不可）、項目と値の範囲を検査、6項目の合計がちょうど1440分、全体で1秒に1件まで。記録の一覧は誰でも読める（集計をブラウザで計算するため）
- ルールを変えたら `firebase deploy --only database`。テストで書いた記録は `firebase database:remove /jikan/r/<id>` で消す
- ほかのツールは今までどおり「入力は外部に送信しない」

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
