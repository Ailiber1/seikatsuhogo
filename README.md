# 生活保護のしらべもの

YouTubeチャンネル「リベル_Liber」の生活保護配信で使う、解説ページと調べものツールを集めたところ。

**公開URL: https://ailiber1.github.io/seikatsuhogo/**

生活保護に関して作ったものは、資料もツールも元データも生成スクリプトも、すべてこのリポジトリで管理する。
バラバラに散らさない。ローカルのフォルダには残さない。

---

## 中身

| ファイル | 種類 | 内容 | 公開URL |
|---|---|---|---|
| `index.html` | 一覧 | 作ったものの入口 | [/](https://ailiber1.github.io/seikatsuhogo/) |
| `sodan.html` | ツール | 生活の相談窓口をさがす（全国1,370か所） | [/sodan.html](https://ailiber1.github.io/seikatsuhogo/sodan.html) |
| `tokurei.html` | ツール | 特例加算しらべ（自分がいくら増えるか） | [/tokurei.html](https://ailiber1.github.io/seikatsuhogo/tokurei.html) |
| `fuyo.html` | 解説 | 生活保護を申請すると家族に通知は行くのか（扶養照会） | [/fuyo.html](https://ailiber1.github.io/seikatsuhogo/fuyo.html) |
| `tokurei-setsumei.html` | 解説 | 生活保護費が10月から上がる。上がらない人もいる理由 | [/tokurei-setsumei.html](https://ailiber1.github.io/seikatsuhogo/tokurei-setsumei.html) |
| `data/` | データ | ページに埋め込む元データ（JSON） | — |
| `scripts/` | スクリプト | 公的資料からデータを作り、ページを生成する | — |

## data/ の中身

| ファイル | 内容 | 出典 |
|---|---|---|
| `madoguchi.json` | 全国の自立相談支援機関 1,370か所（窓口名・住所・電話・メール） | 厚労省が案内する「令和7年度 自立相談支援機関窓口情報」 |
| `kyuchi_by_city.json` | 全1,741市区町村の級地区分 | 厚労省「お住まいの地域の級地を確認」＋総務省「全国地方公共団体コード」 |
| `keika.json` | 生活扶助本体に係る経過的加算（世帯人数×年齢×級地） | 厚労省「生活扶助基準額の算出方法（令和8年4月）」別表(1) |
| `ages.json` | 経過的加算の年齢区分 | 同上 |

## scripts/ の中身

| ファイル | 役割 |
|---|---|
| `fetch_madoguchi.py` | 相談窓口の一覧を取得して `data/madoguchi.json` を作る |
| `gen_madoguchi_tool.py` | `data/madoguchi.json` から `sodan.html` を生成する |

---

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

### ツール
- **開いた直後は結果を出さない。** 配信で使い方を実演するため
- ただし空の画面にはせず、「上で◯◯を選ぶと、ここに△△が出ます」という案内を出す
- プルダウンの先頭は「選んでください」。2段目は1段目が未選択のあいだ押せないようにする
- 入力内容は**ブラウザの中だけで処理し、外部に送信しない**

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
