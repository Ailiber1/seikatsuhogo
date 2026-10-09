#!/usr/bin/env python3
"""blacklist.html の calc() を取り出して node で動かし、決まり（data/blacklist.json）どおりの年月になるか確かめる。

決まり:
  全国銀行個人信用情報センター = 破産手続開始決定の日から7年（7年後の応当日の前日まで）
  CIC = 免責で契約が終わった日から5年 / JICC = 免責確定日付で完済、契約終了後5年以内
月までしか聞かないので、終わりは「開始の年月 + 7年」「免責の年月 + 5年」の年月で比べる。
"""
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = (ROOT / 'blacklist.html').read_text(encoding='utf-8')
m = re.search(r'function calc\(.*?\n}\n', html, re.S)
if not m:
    sys.exit('calc() が見つからない')

# (開始, 免責 or None, いま) -> 期待する (全銀の終わり, CICの終わり, JICCの終わり, 最後に残る機関（同じ月なら全部）, 状態)
# 状態: gone=もう消えた目安 / now=今月ごろ消える / left=まだ残る
CASES = [
    ((2024, 6), (2025, 3), (2026, 10), ('2031-6', '2030-3', '2030-3', '全国銀行個人信用情報センター', 'left')),
    ((2015, 1), (2015, 6), (2026, 10), ('2022-1', '2020-6', '2020-6', '全国銀行個人信用情報センター', 'gone')),
    ((2020, 1), (2022, 6), (2026, 10), ('2027-1', '2027-6', '2027-6', 'CIC・JICC', 'left')),
    ((2019, 12), (2020, 2), (2027, 1), ('2026-12', '2025-2', '2025-2', '全国銀行個人信用情報センター', 'gone')),
    ((2019, 12), (2020, 2), (2026, 12), ('2026-12', '2025-2', '2025-2', '全国銀行個人信用情報センター', 'now')),
    ((2019, 12), (2020, 2), (2026, 11), ('2026-12', '2025-2', '2025-2', '全国銀行個人信用情報センター', 'left')),
    ((2026, 4), None, (2026, 10), ('2033-4', None, None, None, None)),
]

js = m.group(0) + """
const cases = %s;
const res = cases.map(([k, mm, now]) => {
  const r = calc({y: k[0], m: k[1]}, mm ? {y: mm[0], m: mm[1]} : null, {y: now[0], m: now[1]});
  const e = o => o.end ? o.end.y + '-' + o.end.m : null;
  return [e(r.orgs[0]), e(r.orgs[1]), e(r.orgs[2]), r.last ? r.lastNames.join('・') : null, r.last ? (r.last.left < 0 ? 'gone' : r.last.left === 0 ? 'now' : 'left') : null];
});
console.log(JSON.stringify(res));
""" % json.dumps([[list(k), list(mm) if mm else None, list(now)] for k, mm, now, _ in CASES])

out = subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout
got = json.loads(out)
ng = 0
for (k, mm, now, want), g in zip(CASES, got):
    ok = tuple(g) == want
    ng += not ok
    print(('OK ' if ok else 'NG ') + f'開始{k} 免責{mm} いま{now} -> {g}' + ('' if ok else f'  期待 {list(want)}'))
print(f'{len(CASES) - ng}/{len(CASES)} 件一致')
sys.exit(1 if ng else 0)
