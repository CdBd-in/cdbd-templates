#!/usr/bin/env python3
"""CdBd AI 빌더 산출물 — 에디터 데이터 자동 검사 (4-9-5 §3 S11 체크의 실행판)

사용: python3 audit.py <editor.json> [--presets presets.json] [--md out.md] [--json out.json]
  editor.json  = 에디터 fiber의 editor 객체(JSON) — dump.sh 가 추출
  presets.json = 프리셋 어드민 전체 목록(JSON) — 원본 대조(S11-40 원본 결함 구분 · S11-41 · S11-43)에 필요.
                 없으면 원본 대조 체크는 「미측정」으로 남긴다(통과 ❌)
판정 규칙의 정본 = 4-9-5 §3 S11 표. 이 파일은 그 표를 코드로 옮긴 것(체크 ID 동일).
⚙ 표시 임계값을 바꾸면 4-9-5 ⚙ 보정 기록에도 한 줄 남긴다.
"""
import argparse, colorsys, json, re

# ── 기준값 (정본 = 4-9-5 · MD-08-3 · MD-08-2) ─────────────────────────
EDITOR_DEFAULT = ('#FAFAFA', '#292929', '#292929')        # 새 페이지 기본 테마
PRESET_DEFAULT_HEX = ('#6C4CFF', '108,76,255', '108, 76, 255')
# MD-08-3 플레이스홀더 표 + 섹션 원본 견본 값 (최종 페이지에 남으면 안 됨)
PLACEHOLDERS = ['02-000-0000', 'CdBd 라운지', '강남대로 373', '3층 그랜드볼룸', 'cdbd.com',
                'instagram.com/cdbd', 'youtube.com/@cdbd', 'pf.kakao.com/_cdbd', 'blog.naver.com/cdbd',
                '홍우빌딩', 'musinsa.com/products/6625294', '"예약 장소"']
GENERIC_MARKERS = {'✅', '✔️', '✔', '☑️', '✓', '●', '•', '·', '▪️', '▪', '◼️', '■', '-', '—'}
MONO_MARKERS = {'✔', '✓', '●', '•', '·', '▪', '■', '-', '—', '❶', '❷', '❸', '❹', '❺', '①', '②', '③', '④', '⑤'}
EMOJI_RE = re.compile('^[\U0001F300-\U0001FAFF☀-➿⬀-⯿①-⓿■-◿️‍•·\\-—]+$')
TH_BIG, TH_LINE, TH_BOX = 9, 20, 18           # ⚙ S11-49 줄 나누기 기준 (MD-08-3 📱)
TH_GAP = 60                                     # ⚙ S11-42 이웃 카드 보이는 여백 (섹션 사이 = 36＋20 = 56)
TH_VAL = 8                                      # ⚙ S11-47 2열 값 칸 글자 수 (MD-08-3 길이 표)


# ── 읽기 도우미 ─────────────────────────────────────────────────────
def paras(content):
    """Lexical content → [{'items': [('T',text,style,format)|('BR',)], 'align': str}]"""
    try:
        c = json.loads(content)
    except Exception:
        return []
    out = []
    for p in c.get('root', {}).get('children', []):
        items = []

        def walk(n):
            for ch in n.get('children', []) or []:
                t = ch.get('type')
                if t == 'text':
                    items.append(('T', ch.get('text', ''), ch.get('style', '') or '', ch.get('format', 0) or 0))
                elif t == 'linebreak':
                    items.append(('BR',))
                elif ch.get('children'):
                    walk(ch)
        walk(p)
        out.append({'items': items, 'align': p.get('format') or ''})
    return out


def ptext(p): return ''.join(i[1] for i in p['items'] if i[0] == 'T')
def full(ps): return '\n'.join(ptext(p) for p in ps)
def nonempty(ps): return [k for k, p in enumerate(ps) if ptext(p).strip()]
def fs_of(style):
    m = re.search(r'font-size:\s*(\d+)', style or '')
    return int(m.group(1)) if m else None


def num(v, default=16):
    m = re.match(r'^\s*(-?[\d.]+)', str(v))
    return float(m.group(1)) if m else default


def box(s):
    v = [num(x, 0) for x in str(s or '0').split()] or [0]
    if len(v) == 1: v = v * 4
    elif len(v) == 2: v = [v[0], v[1], v[0], v[1]]
    elif len(v) == 3: v = [v[0], v[1], v[2], v[1]]
    return v  # 상 우 하 좌


def has_fill(st): return str(st.get('background') or '').lower() not in ('', 'none', 'transparent')
def has_border(st): return num(st.get('borderWidth') or 0, 0) > 0 and str(st.get('borderStyle') or '') != 'none'
def has_bg(st): return has_fill(st) or has_border(st)
def hexn(h): return str(h or '').upper()


def hsv(h):
    h = hexn(h).lstrip('#')
    if len(h) != 6: return None
    return colorsys.rgb_to_hsv(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def align_of(card_or_item):
    ps = paras(card_or_item.get('content') or '')
    ne = nonempty(ps)
    a = ps[ne[0]]['align'] if ne else ''
    return a or (card_or_item.get('style') or {}).get('textAlign') or 'left'


def cells(b):
    """(라벨, paras, 카드 또는 칸) — 텍스트 카드 본문 + 2열 카드 각 칸"""
    out = []
    if b.get('type') in ('text', 'button') and b.get('content'):
        out.append(('본문', paras(b['content']), b))
    for j, it in enumerate((b.get('multiCard') or {}).get('items', []) or []):
        if it.get('content'):
            out.append((f'칸{j + 1}', paras(it['content']), it))
    return out


def sig(b):
    st = b.get('style') or {}
    return (b.get('type'), b.get('title'), tuple(box(st.get('padding'))), tuple(box(st.get('margin'))))


def is_title(b): return '섹션 타이틀' in str(b.get('title') or '')


def marker_row(b):
    """이모지·기호 칸 + 텍스트 칸의 2열 행이면 (표식, 항목 글) — 아니면 None"""
    items = (b.get('multiCard') or {}).get('items', []) or []
    if b.get('type') != 'multiCard' or len(items) != 2: return None
    a = full(paras(items[0].get('content') or '')).strip()
    t = full(paras(items[1].get('content') or '')).strip()
    return (a, t) if a and t and len(a) <= 3 and EMOJI_RE.match(a) else None


# ── 검사 ────────────────────────────────────────────────────────────
def audit(ed, presets=None):
    F = []

    def flag(cid, sev, msg, where='', route='빌더'):
        # route = 고칠 곳 — 빌더(MD·생성) · 원본(섹션 원본 수정) · 개발 — 정본 = 4-9-5 §7 판별 3갈래
        F.append({'id': cid, 'sev': sev, 'msg': msg, 'where': where, 'route': route})

    th = ed.get('theme') or {}
    base, btn = th.get('base') or {}, th.get('button') or {}
    blocks = ed.get('blocks') or []
    if not blocks and ed.get('pages'):
        blocks = [b for p in sorted(ed['pages'], key=lambda x: x.get('order', 0)) for b in (p.get('blocks') or [])]
    blocks = [b for b in blocks if not b.get('disabled')]
    W = lambda i, b, lab='': f'카드{i + 1} {b.get("title") or b.get("type")}{(" " + lab) if lab else ""}'

    idx = {}
    if presets:
        for p in presets:
            for bb in p.get('blocks') or []:
                idx.setdefault(sig(bb), []).append((p.get('preset_key'), bb))

    # S11-44 무드 미적용 · S11-45 기본값 닮은 팔레트 · S11-13 기본 토큰 잔존
    trip = (hexn(base.get('background')), hexn(base.get('color')), hexn(btn.get('background')))
    if trip == EDITOR_DEFAULT:
        flag('S11-44', 'C', f'무드 미적용 — 페이지 테마가 새 페이지 기본값 그대로 {"/".join(trip)}', '테마')
    else:
        b_, t_, u_ = hsv(trip[0]), hsv(trip[1]), hsv(trip[2])
        if b_ and t_ and u_ and b_[1] <= 0.06 and b_[2] >= 0.93 and t_[2] <= 0.25 and u_[1] >= 0.35 and 0.68 <= u_[0] <= 0.80:
            flag('S11-45', 'M', f'섹션 원본 기본 색을 닮은 팔레트 {"/".join(trip)} — 흰 배경·검정 글자·보라 버튼', '테마')
    raw = json.dumps(blocks, ensure_ascii=False).upper()
    n6c = sum(raw.count(x.upper()) for x in PRESET_DEFAULT_HEX)
    if n6c and hexn(btn.get('background')) != '#6C4CFF':
        flag('S11-13', 'M', f'섹션 원본 기본 보라 #6C4CFF {n6c}곳 잔존', '카드 색')

    # S11-46 견본 값 잔존 (글·링크·주소 전부)
    rawl = json.dumps(blocks, ensure_ascii=False).lower()
    for ph in PLACEHOLDERS:
        if ph.lower() in rawl:
            flag('S11-46', 'C', f'견본 값 {ph.strip(chr(34))} 이 완성 페이지에 남음', '페이지 글·링크·주소', '빌더·개발')

    # S11-39 상단 여백 하한 (최상단 · 배경 카드 묶음 첫 행)
    if blocks and blocks[0].get('type') != 'menu':
        st = blocks[0].get('style') or {}
        top = box(st.get('padding'))[0] + box(st.get('margin'))[0]
        if top < 20:
            flag('S11-39', 'm', f'페이지 맨 위 카드의 위 여백 {top:.0f}px (<20)', W(0, blocks[0]), '원본')
    for i, b in enumerate(blocks):
        st = b.get('style') or {}
        prev = (blocks[i - 1].get('style') or {}) if i else {}
        if has_fill(st) and not has_fill(prev) and b.get('type') in ('text', 'multiCard') and box(st.get('padding'))[0] < 20:
            flag('S11-39', 'm', f'배경 묶음 첫 행 위 안쪽 여백 {box(st.get("padding"))[0]:.0f}px (<20)', W(i, b), '원본')

    for i, b in enumerate(blocks):
        st = b.get('style') or {}
        cands = idx.get(sig(b), [])
        for lab, ps, holder in cells(b):
            ne = nonempty(ps)
            if not ne: continue
            t = full(ps).strip()
            # S11-40 빈 줄 0 — 끝에 남은 빈 줄 · 끝 줄바꿈 · 사이 빈 줄(원본에 없던 것)
            trail = len(ps) - 1 - ne[-1]
            brend = 1 if ps[ne[-1]]['items'] and ps[ne[-1]]['items'][-1][0] == 'BR' else 0
            mids = [k for k in range(ne[0], ne[-1]) if k not in ne]
            if cands:
                oc = [dict((l, p) for l, p, _ in cells(o)).get(lab) for _, o in cands]
                oc = [o for o in oc if o is not None]
                if oc and all(len(o) - 1 - (nonempty(o) or [len(o) - 1])[-1] > 0 for o in oc) and trail:
                    flag('S11-40', 'M', f'끝 빈 줄 {trail}개 — 섹션 원본에도 있음 「{t[:20]}」', W(i, b, lab), '원본')
                    trail = 0
                if oc and mids and all(any(k < len(o) and not ptext(o[k]).strip() for k in mids) for o in oc):
                    mids = []
            if trail or brend or mids:
                flag('S11-40', 'M', f'내용 없는 줄 — 끝 {trail + brend}개 · 사이 {len(mids)}개 「{t[:20]}」', W(i, b, lab))
            # S11-41 여러 줄 칸 = 줄 역할 보존 (원본 줄 수·순서대로)
            if cands:
                oc = [dict((l, p) for l, p, _ in cells(o)).get(lab) for _, o in cands]
                oc = [o for o in oc if o is not None]
                multi = [o for o in oc if len(nonempty(o)) >= 2 and
                         len({(fs_of(x[2]), x[3] & 1) for k in nonempty(o) for x in o[k]['items'] if x[0] == 'T'}) >= 2]
                if oc and len(multi) == len(oc) and len(ne) < min(len(nonempty(o)) for o in multi):
                    n_o = min(len(nonempty(o)) for o in multi)
                    flag('S11-41', 'M', f'여러 줄 칸({n_o}줄)을 {len(ne)}줄에 몰아 씀 「{t[:20]}」', W(i, b, lab))
            # S11-49 한 줄 문구 줄 나누기 (한 줄짜리 칸 · 텍스트 카드만)
            if b.get('type') == 'text' and len(ne) == 1 and not any(x[0] == 'BR' for x in ps[ne[0]]['items']) and len(ps) == 1:
                runs_ = [x for x in ps[ne[0]]['items'] if x[0] == 'T']
                size = max([fs_of(x[2]) or num(st.get('fontSize'), 16) for x in runs_] or [16])
                lim = TH_BIG if size >= 28 else (TH_BOX if has_bg(st) else TH_LINE)
                if size >= 15 and lim < len(t) <= 40:
                    flag('S11-49', 'm', f'{size:.0f}px 한 줄 문구 {len(t)}자 > {lim}자인데 줄바꿈 없음 「{t[:20]}」', W(i, b))

    # S11-47 2열 값 칸 = 짧은 값 (라벨＋값 행의 오른쪽 정렬 값)
    for i, b in enumerate(blocks):
        items = (b.get('multiCard') or {}).get('items', []) or []
        if b.get('type') == 'multiCard' and len(items) == 2 and all(it.get('type') == 'text' for it in items) and not marker_row(b):
            v = items[1]
            vt = full(paras(v.get('content') or '')).strip()
            if align_of(v) == 'right' and (len(vt) > TH_VAL or re.search(r'(다|요)[.!]?$', vt)):
                flag('S11-47', 'M', f'2열 값 칸에 긴 글 {len(vt)}자 「{vt[:20]}」', W(i, b))

    # S11-43 이모지 칸 = 내용에 맞게 · 같은 위계 나열 = 한 종류
    runs, cur = [], []
    for i, b in enumerate(blocks):
        r = marker_row(b)
        if r: cur.append((i, b, r))
        elif cur: runs.append(cur); cur = []
    if cur: runs.append(cur)
    samples = {}
    for (k, (pk, bb)) in ((k, v) for k, vs in idx.items() for v in vs):
        r = marker_row(bb)
        if r: samples.setdefault(k, set()).add(r[0])
    for run in runs:
        marks = [r[0] for _, _, r in run]
        where = f'카드{run[0][0] + 1}~{run[-1][0] + 1}'
        if len(set(marks)) == 1 and marks[0] in GENERIC_MARKERS:
            continue
        kept = [m for (i, b, (m, _)) in run if m in samples.get(sig(b), set())]
        if presets is not None and kept:
            flag('S11-43', 'M', f'섹션 원본 견본 이모지 그대로 {" ".join(kept)} (항목 {len(run)}개)', where)
        elif len({m for m in marks if m in GENERIC_MARKERS}) >= 2:
            flag('S11-43', 'M', f'같은 위계 나열에 체크 표식 여러 종류 {" ".join(marks)}', where)
        elif {m.replace(chr(0xFE0F), '') for m in marks} & MONO_MARKERS and any(m not in MONO_MARKERS for m in marks):
            flag('S11-43', 'm', f'컬러 이모지와 흑백 기호 섞임 {" ".join(marks)}', where)
    if presets is None and runs:
        flag('S11-43', '-', '이모지 견본 대조 미측정(섹션 원본 목록 없음)', '')

    # S11-10 (테두리 버튼) 카드 모서리 = 페이지 버튼 모양
    tr = num(btn.get('borderRadius') if btn.get('borderRadius') is not None else 999, 999)
    for i, b in enumerate(blocks):
        st = b.get('style') or {}
        if b.get('type') == 'button' and has_border(st) and not has_fill(st):
            cr = num(st.get('borderRadius') or 0, 0)
            if not (cr == tr or (cr >= 100 and tr >= 100)):
                flag('S11-10', 'M', f'테두리 버튼 카드 모서리 {cr:.0f}px ≠ 페이지 버튼 모양 {tr:.0f}px', W(i, b))

    # S11-48 장식 없는 섹션 타이틀 ↔ 바로 아래 본문 정렬
    for i, b in enumerate(blocks[:-1]):
        nx = blocks[i + 1]
        if (b.get('type') == 'text' and is_title(b) and not has_bg(b.get('style') or {}) and nx.get('type') == 'text'
                and not is_title(nx) and not has_bg(nx.get('style') or {})):
            ta, na = align_of(b), align_of(nx)
            if ta != na and len(full(paras(nx.get('content') or '')).strip()) >= 8:
                flag('S11-48', 'M', f'섹션 타이틀 {ta} ↔ 본문 {na} 정렬 엇갈림 (둘 다 장식 없음)', f'카드{i + 1}→{i + 2}')

    # S11-42 빠진 카드 자리 여백 겹침 — 이웃 카드의 「보이는」 간격(배경·테두리 카드의 안쪽 여백은 상자 안이라 제외)
    def vbot(x):
        s_ = x.get('style') or {}
        return box(s_.get('margin'))[2] + (0 if has_bg(s_) else box(s_.get('padding'))[2])

    def vtop(x):
        s_ = x.get('style') or {}
        return box(s_.get('margin'))[0] + (0 if has_bg(s_) else box(s_.get('padding'))[0])
    FLOW = ('text', 'multiCard', 'button')
    for i in range(len(blocks) - 1):
        a, c = blocks[i], blocks[i + 1]
        if a.get('type') in FLOW and c.get('type') in FLOW:
            gap = vbot(a) + vtop(c)
            if gap >= TH_GAP:
                flag('S11-42', 'M', f'이웃 카드 사이 보이는 여백 {gap:.0f}px (섹션 사이 56보다 넓음) — 빠진 카드 자리 여백이 겹침',
                     f'카드{i + 1}→{i + 2}', '원본·개발')

    # S11-34 텍스트만 페이지 리듬
    imgs = sum(1 for b in blocks if b.get('type') in ('image', 'gallery', 'youtube', 'profile'))
    bgs = sum(1 for b in blocks if b.get('type') in ('text', 'multiCard') and has_fill(b.get('style') or {}))
    divs = sum(1 for b in blocks if b.get('type') == 'divider')
    if imgs <= 2 and bgs <= 1 and divs <= 3:
        flag('S11-34', 'm', f'글만 이어지는 페이지 — 이미지 {imgs} · 배경 카드 {bgs} · 구분선 {divs}', '페이지')
    return F


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('editor'); ap.add_argument('--presets'); ap.add_argument('--md'); ap.add_argument('--json')
    a = ap.parse_args()
    ed = json.load(open(a.editor))
    pr = json.load(open(a.presets)) if a.presets else None
    F = audit(ed, pr)
    C = sum(f['sev'] == 'C' for f in F); M = sum(f['sev'] == 'M' for f in F); m = sum(f['sev'] == 'm' for f in F)
    score = max(0, 100 - 4 * M - m)
    head = (f"에디터 {ed.get('id')} 「{ed.get('title')}」 — 치명 {C} · 주요 {M} · 경미 {m} · 데이터 점수 {score}"
            f"{' · ❌ 즉시 FAIL' if C else ''}")
    lines = [head] + [f"- [{f['sev']}] {f['id']} {f['msg']} ({f['where']}) → {f['route']}" for f in F]
    print('\n'.join(lines))
    if a.md: open(a.md, 'w').write('\n'.join(lines) + '\n')
    res = {'id': ed.get('id'), 'C': C, 'M': M, 'm': m, 'score': score, 'findings': F}
    if a.json: json.dump(res, open(a.json, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
