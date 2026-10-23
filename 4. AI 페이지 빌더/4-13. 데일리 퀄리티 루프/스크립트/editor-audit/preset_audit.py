#!/usr/bin/env python3
"""섹션 원본 자동 검사 — S3(원본 등록·수정) 관문용 (2026-10-23)

사용: python3 preset_audit.py presets.json [--key sec/bold/hero/01 ...] [--md out.md]
  presets.json = 프리셋 어드민 전체 목록 (dump.sh --presets 로 받음)
  --key        = 이 원본만 검사(새로 등록·수정한 것). 없으면 전체
판정 규칙의 정본 = 4-5 「채택 관문」 ⑥ 지워져도 버티는 여백 · 4-9-5 §3 S11-39·40·42
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit import box, has_bg, has_fill, panels, paras, nonempty, ptext, TH_PANEL  # noqa: E402

DELETABLE = ('image', 'gallery', 'youtube')   # 자료가 없으면 빌더가 지우는 카드
EDGE_KINDS = ('hero', 'header', 'footer')      # 페이지 맨 위·띠 안에서 시작하는 섹션


def vtop(b):
    s = b.get('style') or {}
    return box(s.get('margin'))[0] + (0 if has_bg(s) else box(s.get('padding'))[0])


def vbot(b):
    s = b.get('style') or {}
    return box(s.get('margin'))[2] + (0 if has_bg(s) else box(s.get('padding'))[2])


def kind(p):
    k = str(p.get('preset_key') or '')
    if k.startswith('hdr/'): return 'header'
    if k.startswith('ftr/'): return 'footer'
    return (k.split('/') + ['', '', ''])[2]


def check(p):
    F = []
    bl = [b for b in (p.get('blocks') or []) if not b.get('disabled')]
    key = p.get('preset_key')
    for k, b in enumerate(bl):
        t = b.get('type')
        # ① 가운데 카드가 지워지면 이웃 여백이 겹친다 → 지워지는 카드가 제 여백을 든다
        if t in DELETABLE and 0 < k < len(bl) - 1:
            g = vbot(bl[k - 1]) + vtop(bl[k + 1])
            if g >= 60:
                F.append(('지움-가운데', 'M', f'카드{k + 1}({t})가 빠지면 이웃 간격 {g:.0f}px — 이미지 주변 여백을 이미지 카드로 옮길 것'))
        # ② 맨 위 카드가 지워지면 위 여백이 0 (히어로·헤더·푸터만 — 다른 섹션은 앞 섹션 하단 36이 받아 준다)
        if t in DELETABLE and k == 0 and len(bl) > 1 and kind(p) in EDGE_KINDS and vtop(bl[1]) < 20:
            F.append(('지움-맨위', 'm', f'맨 위 {t}가 빠지면 위 여백 {vtop(bl[1]):.0f}px — 개발 A3(지운 카드 여백 넘기기) 전까지 위험 · 이미지 아래 여백을 글 위 여백으로 옮기면 해소'))
        # ③ 마지막 카드가 지워지면 섹션 하단 36이 사라진다 (원본만으론 못 막음 — 개발 A3 몫)
        if t in DELETABLE and k == len(bl) - 1 and k > 0 and vbot(bl[k - 1]) < 36:
            F.append(('지움-맨아래', 'm', f'마지막 {t}가 빠지면 섹션 아래 여백 {vbot(bl[k - 1]):.0f}px (<36) — 개발 A3 몫'))
        # ⑤ 끝에 남은 빈 줄 · 끝 줄바꿈 (본문과 2열 칸)
        cs = [('본문', b.get('content'))] + [(f'칸{j + 1}', it.get('content')) for j, it in enumerate((b.get('multiCard') or {}).get('items', []) or [])]
        for lab, c in cs:
            if not c: continue
            ps = paras(c); ne = nonempty(ps)
            if not ne: continue
            trail = len(ps) - 1 - ne[-1]
            brend = 1 if ps[ne[-1]]['items'] and ps[ne[-1]]['items'][-1][0] == 'BR' else 0
            if trail or brend:
                F.append(('빈 줄', 'M', f'카드{k + 1} {lab} 끝에 빈 줄 {trail + brend}개 「{ptext(ps[ne[-1]])[:16]}」'))
    # ④ 배경 면(2장↑ 맞붙은 묶음) 첫 행 위 안쪽 여백 ≥12 — 행 간격(8~10)을 위 여백으로 쓰면 위가 눌려 보인다
    for run in panels(bl):
        f0 = bl[run[0]]; t0 = box((f0.get('style') or {}).get('padding'))[0]
        if len(run) >= 2 and f0.get('type') in ('text', 'multiCard') and t0 < TH_PANEL:
            F.append(('면-첫행', 'M', f'카드{run[0] + 1} 배경 면({len(run)}장) 첫 행 위 안쪽 여백 {t0:.0f}px (<{TH_PANEL}) — 리드 문장은 면 밖으로 · 첫 행 위 20'))
    return key, F


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('presets'); ap.add_argument('--key', nargs='*'); ap.add_argument('--md')
    a = ap.parse_args()
    P = json.load(open(a.presets))
    if a.key: P = [p for p in P if p.get('preset_key') in set(a.key)]
    out, tally = [], {}
    for p in P:
        key, F = check(p)
        for cid, sev, msg in F:
            tally[cid] = tally.get(cid, 0) + 1
            out.append(f'- [{sev}] {key} · {cid} — {msg}')
    head = f'섹션 원본 {len(P)}개 검사 — ' + (' · '.join(f'{k} {v}' for k, v in sorted(tally.items())) or '문제 0')
    print(head); print('\n'.join(out))
    if a.md: open(a.md, 'w').write(head + '\n' + '\n'.join(out) + '\n')
    sys.exit(1 if any(' [M] ' in o for o in out) else 0)


if __name__ == '__main__':
    main()
