/*
  まとめページ（index.html）に並ぶカードの一覧。
  新しいツール・解説を足すときは、下の ITEMS に1行足すだけ。並んだ順にカードが出る。

    kind : "tool"（ツール） か "doc"（解説）
    icon : カードの絵文字
    title: 題名（短く）
    desc : 説明（1行ぶん）
    href : ページのファイル名
    kw   : 検索用の言葉（カードには出ない。「家賃」で探した人にも見つかるようにする）
    isNew: true にすると「NEW」が付く（古くなったら外す）
    locked: true にすると「🔐 配信で公開」になり、押しても開かない（配信で紹介するまで。紹介したら消す）
    video: true にすると「▶動画あり」が付く（そのツール・解説を説明する動画を、そのページに置いたとき）
*/
const ITEMS = [
  {kind:"tool", icon:"🛡️", title:"アンチコメ返し", desc:"言われた言葉を選ぶと、法律と国の資料での答えが出る", href:"anti-kaeshi.html", kw:"アンチ 悪口 働け 税金 贅沢 貯金 不正受給 申告 言われた 返し方 批判", isNew:true, locked:true},
  {kind:"doc",  icon:"📕", title:"アンチコメ図鑑", desc:"3年目の私に届いた151件を全部数えた。多い順と事実での答え", href:"anti.html", kw:"アンチ 悪口 コメント 批判 叩かれる 働け 税金 ランキング YouTube 発信", isNew:true, locked:true},
  {kind:"tool", icon:"🛰️", title:"暇人スキャン", desc:"ふだんの1日を国の平均・リスナーとくらべて暇人か判定", href:"hima.html", kw:"暇 ひま 1日 生活時間 過ごし方 睡眠 自由時間 平均 比較 暇人", isNew:true},
  {kind:"tool", icon:"💴", title:"給料いくら残るしらべ", desc:"働いた給料のうち、手元に残る額と差し引かれる額", href:"kyuryo.html", kw:"給料 収入 働く バイト パート 基礎控除 臨時収入 控除", isNew:true},
  {kind:"tool", icon:"🧮", title:"保護費しらべ", desc:"市区町村・人数・年齢から毎月の保護費を計算", href:"hogohi.html", kw:"保護費 家賃 住宅扶助 生活扶助 いくら 級地 もらえる金額", isNew:true},
  {kind:"tool", icon:"📮", title:"追加給付しらべ", desc:"最高裁判決の追加給付、対象か・申し出先は？", href:"tsuika.html", kw:"追加給付 最高裁 判決 申し出 差額 引き下げ", video:true},
  {kind:"tool", icon:"📞", title:"相談窓口をさがす", desc:"全国1,370か所の相談窓口。名前・電話・住所", href:"sodan.html", kw:"相談 窓口 電話 住所 自立相談支援 困りごと"},
  {kind:"tool", icon:"📈", title:"特例加算しらべ", desc:"10月からの引き上げで自分の世帯はいくら増える？", href:"tokurei.html", kw:"特例加算 10月 増額 引き上げ 1500 2500"},
  {kind:"doc",  icon:"🕰️", title:"生活保護は暇じゃない", desc:"3年目の1日を国の平均とくらべた。AIの作業時間も数えると？", href:"hima-setsumei.html", kw:"暇 ひま 1日 生活時間 過ごし方 怠け 睡眠 仕事 AI 平均", isNew:true},
  {kind:"doc",  icon:"⏰", title:"追加給付、申し出ないと0円", desc:"やめた人は2027年7月31日までに申し出が必要", href:"tsuika-setsumei.html", kw:"追加給付 最高裁 期限 申し出 2027 手続き", video:true},
  {kind:"doc",  icon:"🌍", title:"ベーシックインカムは今", desc:"世界の実験・制度化・日本・AIとの関係", href:"basic-income.html", kw:"ベーシックインカム BI 世界 給付付き税額控除 マスク AI 実験"},
  {kind:"doc",  icon:"👨‍👩‍👧", title:"申請すると家族に通知は？", desc:"扶養照会が行かない3つの条件", href:"fuyo.html", kw:"扶養照会 家族 親族 通知 申請 バレる 連絡"},
  {kind:"doc",  icon:"⬆️", title:"10月から保護費が上がる", desc:"上がらない人もいる理由を資料で説明", href:"tokurei-setsumei.html", kw:"特例加算 10月 増額 上がらない 理由"}
];
