#!/usr/bin/env python3
"""preset-index.json → draft75/PRESETS.md (목적 × 스타일 픽리스트) 재생성.
사용: python3 rebuild-picklist.py   (이 파일이 있는 폴더 기준 상대경로)"""
import json, os, datetime, collections

BASE = os.path.dirname(os.path.abspath(__file__))
IDX  = os.path.join(BASE, 'preset-index.json')
OUT  = os.path.join(BASE, '..', 'draft75', 'PRESETS.md')

STYLES = ['미니멀', '에디토리얼', '볼드']
EXPAND = {'미니멀': ['미니멀'], '에디토리얼': ['에디토리얼'], '볼드': ['볼드'],
          '미에': ['미니멀', '에디토리얼'], '미볼': ['미니멀', '볼드'],
          '에볼': ['에디토리얼', '볼드'], '미에볼': STYLES}
STRUCT = ['헤더', '푸터', '섹션타이틀']
ORDER  = ['히어로', '소개', '핵심 정보', '스토리', '안내사항', '나열', '자료',
          '예약', '폼', '구매', '프로모션', '위치 안내', '문의'] + STRUCT

data = json.load(open(IDX, encoding='utf-8'))
buckets = collections.defaultdict(lambda: collections.defaultdict(list))
for e in data:
    grp = e['grp']
    if grp in STRUCT:
        for s in STYLES: buckets[grp][s].append(e)
        continue
    purpose, _, tok = grp.rpartition('-')
    for s in EXPAND.get(tok, [tok]): buckets[purpose][s].append(e)

today = datetime.date.today().isoformat()
L = [f'# 목적 × 스타일 프리셋 픽리스트 ({today} 자동 생성)', '',
     '> ⚠️ 손으로 고치지 말 것 — `preset-index/preset-index.json`에서 `rebuild-picklist.py`로 재생성됩니다.',
     f'> 프리셋 {len(data)}개 (섹션 {len(data)-sum(1 for e in data if e["grp"] in STRUCT)} · 구조 {sum(1 for e in data if e["grp"] in STRUCT)})', '']
for purpose in ORDER + [p for p in buckets if p not in ORDER]:
    if purpose not in buckets: continue
    L.append(f'## {purpose}')
    for s in STYLES:
        rows = sorted(buckets[purpose][s], key=lambda e: e['h'])
        if not rows: continue
        L += ['', f'**{s}** ({len(rows)}개)', '']
        for e in rows:
            L.append(f"- `{e['id']}` {e['name']} h{e['h']} — {e['slots']}")
    L.append('')
open(OUT, 'w', encoding='utf-8').write('\n'.join(L))
print('wrote', os.path.normpath(OUT), '|', len(data), 'presets')
