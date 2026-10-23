#!/usr/bin/env python3
"""CdBd AI 빌더 산출물 — 에디터 데이터 자동 검사 (4-9-5 S11 체크의 실행판)

사용: python3 audit.py <editor.json> [--presets presets.json] [--md out.md]
  editor.json  = 에디터 fiber의 editor 객체(JSON) — dump_editor.js로 추출
  presets.json = 프리셋 어드민 전체 목록(JSON) — 원본 대조 체크(S11-41·43)에 필요. 없으면 「미측정」
판정 규칙의 정본 = 4-9-5 §3 S11 표. 이 파일은 그 표를 코드로 옮긴 것(체크 ID 동일).
"""
import json, sys, re, argparse, colorsys

DEFAULT_THEME = ('#FAFAFA', '#292929', '#292929')
PLACEHOLDERS = ['02-000-0000', 'CdBd 라운지', '강남대로 373', 'cdbd.com', 'instagram.com/cdbd',
                'pf.kakao.com/_cdbd', 'blog.naver.com/cdbd', 'youtube.com/@cdbd']
LOOKALIKE = {('#FFFFFE', '#2B2C34', '#6246EA'), ('#F2F2F2', '#342D2F', '#904FEB'),
             ('#F6F8FA', '#222832', '#694DFC'), ('#FBFBFB', '#13131A', '#8455EA')}
EMOJI_RE = re.compile('^[\U0001F300-\U0001FAFF☀-➿⬀-⯿️‍]+$')

def runs(content):
    try: c = json.loads(content)
    except Exception: return []
    paras = []
    for p in c.get('root', {}).get('children', []):
        items = []
        def walk(n):
            for ch in n.get('children', []) or []:
                t = ch.get('type')
                if t == 'text': items.append(('T', ch.get('text', ''), ch.get('style', ''), ch.get('format', 0)))
                elif t == 'linebreak': items.append(('BR',))
                elif ch.get('children'): walk(ch)
        walk(p)
        paras.append({'items': items, 'align': p.get('textAlign') or p.get('format') or ''})
    return paras

def text_of(paras): return '\n'.join(''.join(i[1] for i in p['items'] if i[0] == 'T') for p in paras)
def fs_of(style):
    m = re.search(r'font-size:\s*(\d+)', style or ''); return int(m.group(1)) if m else None
def pads(s):
    v = [float(x.replace('px', '')) if re.match(r'^-?[\d.]+(px)?$', x) else 0 for x in str(s or '0').split()]
    if not v: v = [0]
    if len(v) == 1: v = v * 4
    elif len(v) == 2: v = [v[0], v[1], v[0], v[1]]
    elif len(v) == 3: v = [v[0], v[1], v[2], v[1]]
    return v
def has_bg(st):
    bg = str(st.get('background') or '').lower(); bw = str(st.get('borderWidth') or '0').replace('px', '')
    try: bwv = float(bw)
    except Exception: bwv = 0
    return bg not in ('', 'none', 'transparent') or bwv > 0
def hexn(h): return str(h or '').upper()
def hsv(h):
    h = hexn(h).lstrip('#')
    if len(h) != 6: return None
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    return colorsys.rgb_to_hsv(r, g, b)

def card_texts(b):
    """(라벨, paras) 목록 — 텍스트 카드 본문 + 2열 카드 각 칸"""
    out = []
    if b.get('type') == 'text' and b.get('content'): out.append(('본문', runs(b['content'])))
    for j, it in enumerate((b.get('multiCard') or {}).get('items', []) or []):
        if it.get('content'): out.append((f'칸{j+1}', runs(it['content'])))
    return out

def sig(b):
    st = b.get('style') or {}
    return (b.get('type'), b.get('title'), '/'.join(map(str, pads(st.get('padding')))), '/'.join(map(str, pads(st.get('margin')))))

def audit(ed, presets=None):
    F = []
    def flag(cid, sev, msg, where=''): F.append({'id': cid, 'sev': sev, 'msg': msg, 'where': where})
    th = ed.get('theme') or {}
    base, btn = th.get('base') or {}, th.get('button') or {}
    blocks = ed.get('blocks') or []
    if not blocks and ed.get('pages'):
        blocks = [b for p in sorted(ed['pages'], key=lambda x: x.get('order', 0)) for b in (p.get('blocks') or [])]
    trip = (hexn(base.get('background')), hexn(base.get('color')), hexn(btn.get('background')))
    # S11-44 무드 미적용
    if trip == DEFAULT_THEME and 'fontSize' in base:
        flag('S11-44', 'C', f'무드 미적용 — 테마가 새 페이지 기본값 그대로 {trip}', '테마')
    # S11-45 기본값 닮은 팔레트
    if trip in LOOKALIKE:
        flag('S11-45', 'M', f'섹션 원본 기본 색을 닮은 팔레트 {trip} — 무드가 안 입혀진 것처럼 보임', '테마')
    # S11-13 기본 토큰 잔존
    raw = json.dumps(blocks).upper()
    n6c = raw.count('#6C4CFF') + raw.count('108,76,255') + raw.count('108, 76, 255')
    if n6c and hexn(btn.get('background')) != '#6C4CFF':
        flag('S11-13', 'M', f'섹션 원본 기본 보라(#6C4CFF) {n6c}곳 잔존', '카드 색')
    # S11-39 최상단 상단 여백
    if blocks:
        b0 = blocks[0]; st = b0.get('style') or {}
        top = pads(st.get('padding'))[0] + pads(st.get('margin'))[0]
        if top < 20 and b0.get('type') != 'menu':
            flag('S11-39', 'm', f'페이지 맨 위 카드의 위 여백 {top:.0f}px (<20)', f'카드1 {b0.get("title")}')
    # S11-40 빈 줄 · S11-50 줄 나누기 · S11-46 견본 값
    alltext = []
    for i, b in enumerate(blocks):
        st = b.get('style') or {}
        for lab, ps in card_texts(b):
            t = text_of(ps); alltext.append(t)
            nonempty = [k for k, p in enumerate(ps) if any(x[0] == 'T' and x[1].strip() for x in p['items'])]
            if ps and nonempty:
                trail = len(ps) - 1 - nonempty[-1]
                emptyruns = sum(1 for p in ps for x in p['items'] if x[0] == 'T' and not x[1].strip())
                if trail > 0 or emptyruns > 0:
                    flag('S11-40', 'M', f'내용 없는 줄 {trail}개 · 빈 글자 조각 {emptyruns}개 — 「{t.strip()[:24]}」', f'카드{i+1} {b.get("title")} {lab}')
            # 한 줄짜리 칸: 문단 1개·줄바꿈 없음
            if len(nonempty) == 1 and not any(x[0] == 'BR' for x in ps[nonempty[0]]['items']):
                runs_ = [x for x in ps[nonempty[0]]['items'] if x[0] == 'T']
                size = max([fs_of(x[2]) or fs_of('font-size:%s' % st.get('fontSize')) or 16 for x in runs_] or [16])
                ln = len(t.strip())
                limit = 9 if size >= 28 else (18 if has_bg(st) else 20)
                if b.get('type') == 'text' and ln > limit and size >= 15 and ln <= 40:
                    flag('S11-50', 'm', f'{size}px 한 줄 문구 {ln}자 > {limit}자인데 줄바꿈 없음 — 「{t.strip()[:24]}」', f'카드{i+1} {b.get("title")}')
        loc = (b.get('location') or {}).get('address') or ''
        if loc: alltext.append(loc)
    page = '\n'.join(alltext)
    for ph in PLACEHOLDERS:
        if ph.lower() in page.lower():
            flag('S11-46', 'C', f'견본 값 「{ph}」이 완성 페이지에 남음', '페이지 글·주소')
    # S11-47 2열 값 칸 길이 (우측정렬 값 칸)
    for i, b in enumerate(blocks):
        items = (b.get('multiCard') or {}).get('items', []) or []
        if b.get('type') == 'multiCard' and len(items) == 2 and all(it.get('type') == 'text' for it in items):
            v = items[1]; al = (v.get('style') or {}).get('textAlign')
            vt = text_of(runs(v.get('content') or '')).strip()
            if al == 'right' and (len(vt) > 8 or re.search(r'(다|요)\.?$', vt)):
                flag('S11-47', 'M', f'2열 값 칸에 긴 글 {len(vt)}자 — 「{vt[:24]}」', f'카드{i+1}')
    # S11-48 테두리 버튼 모서리 ≠ 테마 버튼 모양
    tr = str(btn.get('borderRadius') or '999px')
    for i, b in enumerate(blocks):
        st = b.get('style') or {}
        if b.get('type') == 'button' and has_bg(st) and str(st.get('background') or '').lower() in ('', 'none', 'transparent'):
            cr = str(st.get('borderRadius') or '0px')
            if cr != tr and not (tr == '999px' and cr in ('999px', '9999px')):
                flag('S11-48', 'M', f'테두리 버튼의 카드 모서리 {cr} ≠ 페이지 버튼 모양 {tr}', f'카드{i+1} {b.get("title")}')
    # S11-49 섹션 타이틀 ↔ 바로 아래 본문 정렬
    for i, b in enumerate(blocks[:-1]):
        if b.get('type') == 'text' and '섹션 타이틀' in str(b.get('title')) and not has_bg(b.get('style') or {}):
            nx = blocks[i+1]
            if nx.get('type') in ('text', 'multiCard') and not has_bg(nx.get('style') or {}) and '섹션 타이틀' not in str(nx.get('title')):
                ta = (runs(b.get('content') or '') or [{'align': ''}])[0]['align'] or (b.get('style') or {}).get('textAlign')
                if nx.get('type') == 'text': na = (runs(nx.get('content') or '') or [{'align': ''}])[0]['align'] or (nx.get('style') or {}).get('textAlign')
                else: na = (nx.get('multiCard') or {}).get('align') or ''
                if ta and na and ta != na and nx.get('type') == 'text':
                    flag('S11-49', 'M', f'섹션 타이틀 {ta} ↔ 본문 {na} 정렬 엇갈림', f'카드{i+1}→{i+2}')
    # S11-42 지운 카드 자리 공백 (이웃 텍스트 카드 여백 합)
    for i in range(len(blocks) - 1):
        a, c = blocks[i], blocks[i+1]
        if a.get('type') == 'text' and c.get('type') == 'text':
            gap = pads((a.get('style') or {}).get('padding'))[2] + pads((a.get('style') or {}).get('margin'))[2] + pads((c.get('style') or {}).get('padding'))[0] + pads((c.get('style') or {}).get('margin'))[0]
            if gap >= 80:
                flag('S11-42', 'M', f'이웃 카드 사이 여백 {gap:.0f}px — 빠진 이미지 자리 의심', f'카드{i+1}→{i+2}')
    # S11-34 텍스트만 리듬
    imgs = sum(1 for b in blocks if b.get('type') in ('image', 'gallery', 'youtube'))
    bgsec = sum(1 for b in blocks if b.get('type') in ('text', 'multiCard') and has_bg(b.get('style') or {}))
    divs = sum(1 for b in blocks if b.get('type') == 'divider')
    if imgs <= 2 and bgsec <= 1 and divs <= 3:
        flag('S11-34', 'm', f'글만 이어지는 페이지 — 이미지 {imgs} · 면 {bgsec} · 구분선 {divs}', '페이지')
    # 원본 대조 체크 (S11-41 여러 줄 칸 · S11-43 견본 이모지)
    if presets:
        idx = {}
        for p in presets:
            for bb in p.get('blocks') or []: idx.setdefault(sig(bb), []).append(bb)
        for i, b in enumerate(blocks):
            cands = idx.get(sig(b), [])
            if not cands: continue
            o = cands[0]
            pairs = [(card_texts(o), card_texts(b))]
            for (lo, po), (lb, pb) in zip(*pairs) if False else zip(card_texts(o), card_texts(b)):
                ro = [x for p in po for x in p['items'] if x[0] == 'T' and x[1].strip()]
                rb = [x for p in pb for x in p['items'] if x[0] == 'T' and x[1].strip()]
                styles_o = {(fs_of(x[2]), x[3] & 1) for x in ro}
                if len(ro) >= 2 and len(styles_o) >= 2 and len(rb) == 1 and not EMOJI_RE.match(''.join(x[1] for x in ro[:1]).strip()):
                    flag('S11-41', 'M', f'여러 줄 칸({len(ro)}줄)을 한 줄에 몰아 씀 — 「{rb[0][1][:24]}」', f'카드{i+1} {b.get("title")} {lb}')
            if b.get('type') == 'multiCard':
                io = (o.get('multiCard') or {}).get('items', []) or []
                ib = (b.get('multiCard') or {}).get('items', []) or []
                if len(io) == len(ib) == 2:
                    eo = text_of(runs(io[0].get('content') or '')).strip(); eb = text_of(runs(ib[0].get('content') or '')).strip()
                    to = text_of(runs(io[1].get('content') or '')).strip(); tb = text_of(runs(ib[1].get('content') or '')).strip()
                    if eo and EMOJI_RE.match(eo) and eo == eb and to != tb:
                        flag('S11-43', 'm', f'원본 견본 이모지 {eb} 그대로 — 항목 「{tb[:20]}」', f'카드{i+1}')
    else:
        flag('S11-41/43', '-', '원본 대조 미측정(프리셋 목록 없음)', '')
    return F

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('editor'); ap.add_argument('--presets'); ap.add_argument('--md')
    a = ap.parse_args()
    ed = json.load(open(a.editor)); pr = json.load(open(a.presets)) if a.presets else None
    F = audit(ed, pr)
    C = sum(1 for f in F if f['sev'] == 'C'); M = sum(1 for f in F if f['sev'] == 'M'); m = sum(1 for f in F if f['sev'] == 'm')
    score = max(0, 100 - 4 * M - m)
    head = f"에디터 {ed.get('id')} 「{ed.get('title')}」 — 치명 {C} · 주요 {M} · 경미 {m} · 데이터 점수 {score}{' · ❌ 즉시 FAIL' if C else ''}"
    lines = [head] + [f"- [{f['sev']}] {f['id']} {f['msg']} ({f['where']})" for f in F]
    out = '\n'.join(lines); print(out)
    if a.md: open(a.md, 'w').write(out + '\n')
    print(json.dumps({'id': ed.get('id'), 'C': C, 'M': M, 'm': m, 'score': score}, ensure_ascii=False))

if __name__ == '__main__': main()
