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
  {kind:"tool", icon:"🗾", title:"住む場所の暮らしやすさしらべ", desc:"市区町村を選ぶと、保護費と地域で差が出る出費（物価・ごみ袋など）。52都市ランキングも", href:"chiiki.html", kw:"地域 住む場所 引っ越し 地域差 ランキング 暮らしやすい 大変 級地 冬季加算 灯油 暖房 物価 ごみ袋 ゴミ袋 有料 減免 車 ガソリン 水道 家賃 北海道 北見", locked:true},
  {kind:"doc",  icon:"🏘️", title:"同じ生活保護でも、住む場所でこんなに違う", desc:"北見市のごみ袋135円から。物価・灯油・車・ごみ袋・水道を52都市で比べた", href:"chiiki-setsumei.html", kw:"地域 住む場所 地域差 ランキング 暮らしやすい 大変 級地 冬季加算 灯油 暖房 物価 ごみ袋 ゴミ袋 135円 北見 札幌 北海道 車 ガソリン 水道 家賃", locked:true},
  {kind:"tool", icon:"🧭", title:"失業・低収入チェック", desc:"失業給付は何日・1日いくら？働いていても基準より何円少ない？", href:"shitsugyo.html", kw:"失業 失業保険 失業給付 雇用保険 基本手当 何日 いくら 解雇 倒産 リストラ 退職 自己都合 会社都合 低収入 給料 手取り 年収 働きながら 求職者支援 住居確保給付金"},
  {kind:"doc",  icon:"🪜", title:"仕事を失っても、生活保護を頼っていい", desc:"失業者180万人。クビにならないは本当？3段の支えと、働いていても受けられる理由", href:"shitsugyo-setsumei.html", kw:"失業 失業者 失業率 クビ 解雇 倒産 希望退職 AI 雇用保険 求職者支援 住居確保給付金 働きながら 年収250万 権利 恥ずかしい", video:true},
  {kind:"tool", icon:"🎯", title:"生活保護イメージ当てクイズ", desc:"受けているのはどんな人？5問に予想で答えて、国の数字と答え合わせ", href:"naiwake-quiz.html", kw:"クイズ イメージ 誤解 怠け者 働かない 高齢者 若者 割合 内訳 何割 どんな人 ひとり暮らし 何年 当てる", locked:true},
  {kind:"doc",  icon:"👥", title:"生活保護は怠け者ばかり？", desc:"半分以上は高齢者、4分の1は障害・病気。受けている人の内訳を国のデータで", href:"naiwake-setsumei.html", kw:"怠け者 働かない 働けるのに 誤解 イメージ 内訳 高齢者 障害 傷病 母子 その他の世帯 年齢 若者 割合 ひとり暮らし 受給期間 理由 データ 統計", locked:true},
  {kind:"tool", icon:"🚪", title:"ためらう理由チェック", desc:"使っていない理由は本当に壁？国の原文で確かめる。線より下かも計算", href:"tamerai.html", kw:"ためらう 迷う 恥ずかしい 家族 バレる 貯金 持ち家 車 働いている 窓口 断られた 水際 書類 住所 対象 受けられる 基準 最低生活費 捕捉率", isNew:true},
  {kind:"doc",  icon:"🔍", title:"使えている人は2割だけ？", desc:"基準より収入が少ないのに、生活保護を使っていない世帯が多い理由", href:"hosoku-setsumei.html", kw:"捕捉率 2割 8割 受けていない 使っていない 割合 推計 国会 申請 恥ずかしい 家族 窓口 水際 権利 ためらう", isNew:true, video:true},
  {kind:"tool", icon:"📅", title:"ブラックリスト、いつ消える？しらべ", desc:"自己破産の時期を選ぶと、3つの信用情報機関で記録がいつまで残るか", href:"blacklist.html", kw:"ブラックリスト 自己破産 信用情報 CIC JICC 銀行 いつ消える 何年 クレジットカード 作れる 審査 免責"},
  {kind:"doc",  icon:"🌱", title:"自己破産は人生の終わりじゃなかった", desc:"経験者の記録と、破産後のカード事情（ブラックリストは何年？）", href:"jikohasan-setsumei.html", kw:"自己破産 借金 債務整理 免責 ブラックリスト 信用情報 クレジットカード デビットカード 法テラス 返済", video:true},
  {kind:"tool", icon:"🐷", title:"貯金の境目しらべ", desc:"申請のとき、貯金はいくらまで残せる？車や家電は？", href:"chokin.html", kw:"貯金 預金 手持金 申請 いくらまで 残せる 使い切る 車 家電 保険 持ち家 売る 資産"},
  {kind:"doc",  icon:"🏦", title:"受けられる貯金の境目", desc:"3年目の申請の実体験と国の決まり。家具・家電は売らなくていい", href:"chokin-setsumei.html", kw:"貯金 預金 手持金 申請 5万円 半分 家具 家電 車 保険 持ち家 売る 資産"},
  {kind:"tool", icon:"🛡️", title:"アンチコメ返し", desc:"言われた言葉を選ぶと、法律と国の資料での答えが出る", href:"anti-kaeshi.html", kw:"アンチ 悪口 働け 税金 贅沢 貯金 不正受給 申告 言われた 返し方 批判"},
  {kind:"doc",  icon:"📕", title:"アンチコメ図鑑", desc:"3年目の私に届いた151件を全部数えた。多い順と事実での答え", href:"anti.html", kw:"アンチ 悪口 コメント 批判 叩かれる 働け 税金 ランキング YouTube 発信"},
  {kind:"tool", icon:"🛰️", title:"暇人スキャン", desc:"ふだんの1日を国の平均・リスナーとくらべて暇人か判定", href:"hima.html", kw:"暇 ひま 1日 生活時間 過ごし方 睡眠 自由時間 平均 比較 暇人"},
  {kind:"tool", icon:"💴", title:"給料いくら残るしらべ", desc:"働いた給料のうち、手元に残る額と差し引かれる額", href:"kyuryo.html", kw:"給料 収入 働く バイト パート 基礎控除 臨時収入 控除"},
  {kind:"tool", icon:"🧮", title:"保護費しらべ", desc:"市区町村・人数・年齢から毎月の保護費を計算", href:"hogohi.html", kw:"保護費 家賃 住宅扶助 生活扶助 いくら 級地 もらえる金額"},
  {kind:"tool", icon:"📮", title:"追加給付しらべ", desc:"最高裁判決の追加給付、対象か・申し出先は？", href:"tsuika.html", kw:"追加給付 最高裁 判決 申し出 差額 引き下げ", video:true},
  {kind:"tool", icon:"📞", title:"相談窓口をさがす", desc:"全国1,370か所の相談窓口。名前・電話・住所", href:"sodan.html", kw:"相談 窓口 電話 住所 自立相談支援 困りごと"},
  {kind:"tool", icon:"📈", title:"特例加算しらべ", desc:"10月からの引き上げで自分の世帯はいくら増える？", href:"tokurei.html", kw:"特例加算 10月 増額 引き上げ 1500 2500"},
  {kind:"doc",  icon:"🕰️", title:"生活保護は暇じゃない", desc:"3年目の1日を国の平均とくらべた。AIの作業時間も数えると？", href:"hima-setsumei.html", kw:"暇 ひま 1日 生活時間 過ごし方 怠け 睡眠 仕事 AI 平均"},
  {kind:"doc",  icon:"⏰", title:"追加給付、申し出ないと0円", desc:"やめた人は2027年7月31日までに申し出が必要", href:"tsuika-setsumei.html", kw:"追加給付 最高裁 期限 申し出 2027 手続き", video:true},
  {kind:"doc",  icon:"🌍", title:"ベーシックインカムは今", desc:"世界の実験・制度化・日本・AIとの関係", href:"basic-income.html", kw:"ベーシックインカム BI 世界 給付付き税額控除 マスク AI 実験"},
  {kind:"doc",  icon:"👨‍👩‍👧", title:"申請すると家族に通知は？", desc:"扶養照会が行かない3つの条件", href:"fuyo.html", kw:"扶養照会 家族 親族 通知 申請 バレる 連絡"},
  {kind:"doc",  icon:"⬆️", title:"10月から保護費が上がる", desc:"上がらない人もいる理由を資料で説明", href:"tokurei-setsumei.html", kw:"特例加算 10月 増額 上がらない 理由"}
];
