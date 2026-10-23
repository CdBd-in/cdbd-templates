#!/usr/bin/env python3
"""섹션 원본 자동 검사 — S3(원본 등록·수정) 관문용 (2026-10-23)

사용: python3 preset_audit.py presets.json [--key sec/bold/hero/01 ...] [--md out.md]
  presets.json = 프리셋 어드민 전체 목록 (dump.sh --presets 로 받음)
  --key        = 이 원본만 검사(새로 등록·수정한 것). 없으면 전체
판정 규칙의 정본 = 4-5 「채택 관문」 ⑥ 지워져도 버티는 여백(맨 위·가운데·맨 아래·배경 면) · 4-9-5 §3 S11-39·40·42
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit import box, has_bg, has_fill, height_pad, panels, paras, nonempty, ptext, TH_PANEL  # noqa: E402

DELETABLE = ('image', 'gallery', 'youtube')   # 자료가 없으면 빌더가 지우는 카드
EDGE_KINDS = ('hero', 'header', 'footer')      # 페이지 맨 위·띠 안에서 시작하는 섹션


def vtop(b):
    s = b.get('style') or {}
    return box(s.get('margin'))[0] + (0 if has_bg(s) else box(s.get('padding'))[0])


def vbot(b):
    s = b.get('style') or {}
    return box(s.get('margin'))[2] + (0 if has_bg(s) else box(s.get('padding'))[2])


def touching_band(a, b):
    """두 카드가 같은 배경색으로 바깥 여백 없이 맞붙었나 (안쪽 여백끼리 옮겨도 보이는 모습이 같다)"""
    sa, sb = a.get('style') or {}, b.get('style') or {}
    return has_fill(sa) and has_fill(sb) and str(sa.get('background')) == str(sb.get('background')) \
        and box(sa.get('margin'))[2] == 0 and box(sb.get('margin'))[0] == 0


def movable(card, nb, side):
    """지워질 카드(card)의 이웃(nb) 쪽 여백 중, 보이는 간격을 바꾸지 않고 이웃으로 옮길 수 있는 양
    side = 'bottom'(맨 위 카드 → 다음 카드로) | 'top'(맨 아래 카드 → 앞 카드로)"""
    s = card.get('style') or {}
    i = 2 if side == 'bottom' else 0
    m = box(s.get('margin'))[i]
    pd = box(s.get('padding'))[i]
    inner = pd if (not has_bg(s) or touching_band(*((card, nb) if side == 'bottom' else (nb, card)))) else 0
    return m + inner


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
        # ② 맨 위 카드가 지워지면 그 위 여백도 같이 빠진다 → 카드 아래 여백을 다음 글 카드 위 여백으로 옮겨 둔다
        #    (보이는 간격은 그대로 · 같은 배경 면 안이면 안쪽 여백끼리 · 2026-10-23 원본 36개 반영)
        if t in DELETABLE and k == 0 and len(bl) > 1 and bl[1].get('type') not in DELETABLE:
            mv = movable(b, bl[1], 'bottom')
            if mv > 0:
                F.append(('지움-맨위', 'M', f'맨 위 {t}의 아래 여백 {mv:.0f}px를 다음 카드 위 여백으로 옮길 것 — 그대로면 {t}가 빠질 때 다음 카드 위 여백 {vtop(bl[1]):.0f}px만 남는다'))
            else:
                s1 = bl[1].get('style') or {}
                # 배경 띠가 섹션 맨 위에 닿는 건 정상 → 띠 안 글의 위 안쪽 여백으로 잰다
                top = box(s1.get('padding'))[0] + box(s1.get('margin'))[0] if has_bg(s1) else vtop(bl[1])
                if kind(p) in EDGE_KINDS and top < 20:
                    F.append(('지움-맨위', 'm', f'맨 위 {t}가 빠지면 위 여백 {top:.0f}px — 옮길 여백이 없어 보이는 간격을 바꾸지 않고는 못 고침'))
        # ③ 마지막 카드가 지워지면 섹션 하단 36도 같이 빠진다 → 카드 위 여백은 앞 글 카드 아래 여백으로 옮겨 두고, 그래도 36 미만이면 기록만
        if t in DELETABLE and k == len(bl) - 1 and k > 0 and bl[k - 1].get('type') not in DELETABLE:
            mv = movable(b, bl[k - 1], 'top')
            if mv > 0:
                F.append(('지움-맨아래', 'M', f'마지막 {t}의 위 여백 {mv:.0f}px를 앞 카드 아래 여백으로 옮길 것'))
            elif vbot(bl[k - 1]) < 36:
                F.append(('지움-맨아래', 'm', f'마지막 {t}가 빠지면 섹션 아래 여백 {vbot(bl[k - 1]):.0f}px (<36) — 옮길 여백이 없어 보이는 간격을 바꾸지 않고는 못 고침'))
        # ⑤ 끝에 남은 빈 줄 · 끝 줄바꿈 (본문과 2열 칸)
        cs = [('본문', b.get('content'))] + [(f'칸{j + 1}', it.get('content')) for j, it in enumerate((b.get('multiCard') or {}).get('items', []) or [])]
        for lab, c in cs:
            if not c: continue
            ps = paras(c); ne = nonempty(ps)
            if not ne: continue
            trail = 0 if height_pad(b, ps) else len(ps) - 1 - ne[-1]
            brend = 1 if ps[ne[-1]]['items'] and ps[ne[-1]]['items'][-1][0] == 'BR' else 0
            if trail or brend:
                F.append(('빈 줄', 'M', f'카드{k + 1} {lab} 끝에 빈 줄 {trail + brend}개 「{ptext(ps[ne[-1]])[:16]}」'))
    # ④ 배경 면(2장↑ 맞붙은 묶음) 첫 행 위 안쪽 여백 ≥12 — 행 간격(8~10)을 위 여백으로 쓰면 위가 눌려 보인다
    for run in panels(bl):
        f0 = bl[run[0]]; t0 = box((f0.get('style') or {}).get('padding'))[0]
        if len(run) >= 2 and f0.get('type') in ('text', 'multiCard') and t0 < TH_PANEL:
            F.append(('면-첫행', 'M', f'카드{run[0] + 1} 배경 면({len(run)}장) 첫 행 위 안쪽 여백 {t0:.0f}px (<{TH_PANEL}) — 리드 문장은 면 밖으로 · 첫 행 위 20'))
    # ⑥ 배경 면 맨 위 카드가 지워질 카드면, 그 다음 글 카드 위 안쪽 여백이 면 첫 행 여백이 된다 → 카드 아래 안쪽 여백을 글 위로 옮겨 둔다
    for run in panels(bl):
        if len(run) < 2 or run[0] == 0: continue          # 섹션 맨 위는 ②가 본다
        f0, f1 = bl[run[0]], bl[run[1]]
        t1 = box((f1.get('style') or {}).get('padding'))[0]
        if f0.get('type') in DELETABLE and f1.get('type') in ('text', 'multiCard') and t1 < TH_PANEL:
            F.append(('지움-면첫행', 'M', f'카드{run[0] + 1} 배경 면 맨 위 {f0.get("type")}가 빠지면 글이 면 위쪽에 붙는다(위 안쪽 여백 {t1:.0f}px) — {f0.get("type")} 아래 안쪽 여백을 글 위로 옮길 것'))
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
