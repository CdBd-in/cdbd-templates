# -*- coding: utf-8 -*-
"""TC50 오프라인 스코어러 — 4-9-5 체크 중 compact 스키마에서 판정 가능한 것만 구현.
사용: python3 score.py  (tc50 폴더에서)  → results.json + 콘솔 요약
판정식 출처 = 4-9-5 §3. 여기서 판정 불가한 체크는 구현하지 않음(결과에 '미구현' 명단).
"""
import json, re, glob, unicodedata, collections, os

HERE = os.path.dirname(os.path.abspath(__file__))

TOPICS25 = {  # 4-3 §3 (2026-10-13)
 '1-①','1-②','1-③','1-④',
 '2-①','2-②','2-③','2-④',
 '3-①','3-②',
 '4-①','4-②','4-③','4-④','4-⑤','4-⑥',
 '5-①','5-②','5-③','5-④','5-⑤','5-⑥',
 '6-①','6-②','6-③','6-④',
}
PURPOSES = {'P1','P2','P3','P4','P5','P6'}

# ---------- §2-C 사실 토큰 추출기 ----------
PATS = {
 'date': r'(?:\d{4}[.\-/년]\s?)?\d{1,2}\s?[월./-]\s?\d{1,2}\s?일?',
 'time': r'\d{1,2}:\d{2}|(?:오전|오후)\s?\d{1,2}시(?:\s?\d{1,2}분|\s?반)?',
 'money': r'[\d,]+\s?원|₩\s?[\d,]+|\d+(?:\.\d+)?\s?만\s?원',
 'phone': r'0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',
 'account': r'\d{2,6}-\d{2,6}-\d{2,6}(?:-\d{1,6})?',
 'email': r'[\w.+-]+@[\w-]+\.[\w.]+',
 'url': r'https?://\S+',
 'qty': r'\d+\s?(?:명|석|개|팀|부)',
}

def norm(s):
    s = unicodedata.normalize('NFKC', s or '')
    return re.sub(r'[\s,./\-년월일원₩:~]', '', s)

def tokens(text):
    out = set()
    if not text: return out
    for kind, pat in PATS.items():
        for m in re.findall(pat, text):
            n = norm(m)
            if kind == 'date':
                n = re.sub(r'^(19|20)\d{2}', '', n)  # 연도 생략형 접기
            if len(n) >= 2:
                out.add((kind, n))
    return out

def pool_texts(case):
    """AI가 읽을 수 있는 입력 텍스트 전부 (fetched:false URL 본문 제외)"""
    t = [case['in'].get('text','')]
    for m in case['in'].get('materials', []):
        if m.get('type') == 'url':
            t.append(m.get('value',''))  # URL 문자열 자체는 보임
            if m.get('fetched'): t.append(m.get('text',''))
        else:
            t.append(m.get('parsed_text') or m.get('text') or m.get('ocr_text') or '')
            t.append(m.get('name',''))
    return '\n'.join(t)

def filled_texts(case):
    return '\n'.join(str(f.get('value','')) for f in case['in'].get('filled',[]) if f.get('action') in ('fill','fill_partial'))

# ---------- 체크 엔진 ----------
class R:
    def __init__(self): self.hits = []
    def add(self, cid, sev, detail):
        self.hits.append({'check': cid, 'sev': sev, 'detail': detail[:160]})

def body_lines(desc):
    lines = (desc or '').split('\n')
    return lines[0] if lines else '', lines[1:]

def check_case(c):
    r = R()
    IN = pool_texts(c); INtok = tokens(IN)
    FILLED = filled_texts(c); FILLEDtok = tokens(FILLED)
    o = c.get('out', {}); g = c['in'].get('gold', {})
    desc = o.get('desc','')
    title_line, rest = body_lines(desc)
    rest_txt = '\n'.join(rest)

    # --- S1 ---
    bad = [t for t in tokens(desc) - INtok if t[0] != 'url']
    if bad: r.add('S1-01','C', f'설명에 지어낸 사실 {bad[:4]}')
    if re.search(r'^#|\*\*', desc, re.M) or re.search(r'^[-*–] ', desc, re.M):
        r.add('S1-02','M','마크다운/비표준 글머리')
    bullets = [l for l in desc.split('\n') if re.match(r'^\s*[・\-*•]', l)]
    if any(not l.startswith('・ ') for l in bullets): r.add('S1-03','M','글머리 ≠ 「・ 」')
    if re.search(r'\n{3,}', desc): r.add('S1-04','m','연속 빈 줄')
    if not title_line.strip() or (len(desc.split('\n'))>1 and desc.split('\n')[1].strip()!=''):
        r.add('S1-05','M','짜임(제목/빈줄) 불일치')
    if '페이지' in title_line: r.add('S1-06','M','제목에 「페이지」')
    for l in bullets:
        if l.startswith('・ ') and not re.match(r'^・ .{1,14}: .+$', l):
            r.add('S1-07','M', f'항목 형식 위반: {l[:40]}'); break
    run=0; mx=0
    for l in desc.split('\n'):
        run = run+1 if l.startswith('・') else 0; mx=max(mx,run)
    if mx>6: r.add('S1-08','m', f'연속 항목 {mx}개')
    if re.search(r'여러분|고객님|드립니다', rest_txt): r.add('S1-09','M','방문자 호칭/인사')
    if re.search(r'습니다\.', rest_txt): r.add('S1-10','m','합쇼체')
    if re.search(r'\?|아마|것 같아요', re.sub(PATS['url'],'',desc)): r.add('S1-11','M','질문·추측')
    if re.search(r'초대·예약|상세페이지|히어로|섹션 목적|원페이지형', desc): r.add('S1-12','M','내부 분류어')
    if re.search(r'・ ?참고 ?:', desc): r.add('S1-13','m','「참고:」 라벨')
    if re.search(r'올려주신|첨부하신|자료에 따르면', desc): r.add('S1-14','M','자료 전제 문구')

    # --- S2 ---
    topic = o.get('topic','')
    if topic not in TOPICS25: r.add('S2-01','C', f'주제 코드 비실재 {topic}')
    elif topic != g.get('topic'): r.add('S2-01','M', f'주제 골든 불일치 {topic}≠{g.get("topic")}')
    pc = o.get('purpose_class',{})
    extras = pc.get('extra',[])
    if pc.get('base') not in PURPOSES or len(extras)>2 or any(e not in PURPOSES for e in extras) or pc.get('base') in extras:
        r.add('S2-02','C','목적 분류 형식 위반')
    vis = ' '.join([o.get('purpose_text',''), o.get('target',''), desc] + [ch.get('문구','') for ch in o.get('chips',[])])
    if re.search(r'\d-[①②③④⑤⑥]|(?<![A-Za-z])P[1-6](?![0-9A-Za-z])', vis): r.add('S2-04','C','내부 코드 노출')
    pt = o.get('purpose_text','')
    if '?' in pt or not pt.rstrip().endswith('요.') : r.add('S2-05','m','목적 문구 형식')

    # --- S3 ---
    if o.get('type',{}).get('값') != g.get('type'): r.add('S3-02','M', f'유형 골든 불일치')

    # --- S4 ---
    comp = o.get('comp',[])
    unknown = [s['name'] for s in comp if s.get('name') not in INDEX_NAMES]
    if unknown: r.add('S4-01','C', f'비실재 섹션 {unknown[:3]}')
    if comp and '히어로' not in comp[0].get('목적',''): r.add('S4-02','C', f'최상단 ≠ 히어로 ({comp[0].get("목적")})')
    moku = [s.get('목적') for s in comp]
    if moku.count('문의') > 1: r.add('S4-12','M','문의 섹션 2개+')

    # --- S5 (샘플 단계만) ---
    for step in o.get('q',[]):
        for k in step.get('칸',[]):
            lab = k.get('라벨','')
            if re.search(r'label|LABEL|EYEBROW|CTA|히어로|섹션', lab + step.get('주어','') + str(k.get('플레이스홀더',''))):
                r.add('S5-05','C', f'제작 용어 노출 {lab}')
            if not (2 <= len(lab) <= 6) or re.search(r'(하기|입력|해 주세요)$', lab):
                r.add('S5-04','M', f'라벨 형식 {lab}')
            if '필수' not in k: r.add('S5-13','M', f'필수/선택 미표기 {lab}')

    # --- S6 ---
    for s in o.get('state',[]):
        st = s.get('상태','')
        if st not in {'미리 채움','비어 있음','못 채움'}: r.add('S6-01','C', f'상태값 {st}')
        v = str(s.get('값',''))
        if st == '미리 채움':
            btok = [t for t in tokens(v) - INtok if t[0] != 'url']
            if btok: r.add('S6-02','C', f'{s.get("칸")} 지어낸 값 {btok[:2]}')
            if re.search(r'추후 공지|문의 바랍니다|미정|TBD', v): r.add('S6-04','M', f'{s.get("칸")} 임시 문구')
            if re.match(r'^예: ', v): r.add('S6-05','m','「예: 」 유출')

    # --- S7 ---
    for rc in o.get('react',[]):
        msg = rc.get('문구','')
        if not msg: continue
        if re.search(r'AI|채운 칸|반응|표시', msg): r.add('S7-03','C','내부 판단 유출')
        if msg.count('.') > 1 or not re.search(r'요[.!]?\s*\S{0,2}$', msg): r.add('S7-04','m', f'반응 형식 {msg[:30]}')
        if re.search(r'\d+개|알찬|풍성한|꼼꼼한|탄탄한|수고|잘하셨|완벽해요|대단해요', msg): r.add('S7-05','M', f'금지어 {msg[:30]}')
        if g.get('heavy') and re.search(r'[\U0001F300-\U0001FAFF✨🎉❤️]', msg): r.add('S7-06','M','무거운 소식에 이모지')

    # --- S8 ---
    th = o.get('mood',{}).get('테마',{})
    if th.get('버튼') not in {'원형','각진','둥근'} or th.get('모서리') not in {'각진','둥근'} or not (isinstance(th.get('여백'),int) and th['여백']>=20):
        r.add('S8-06','C', f'테마 값 {th}')

    # --- S9 ---
    rec = o.get('record',[])
    if len(rec)>=3:
        if len({x.get('명도') for x in rec}) == 1: r.add('S9-02','M','3안 명도 동일')
        if len({x.get('액센트계열') for x in rec}) < 2: r.add('S9-03','M','액센트 계열 1종')
        # 같은 목적 섹션 3안 동일 (name prefix = 목적)
        per = [set(x.get('섹션',[])) for x in rec]
        common = per[0] & per[1] & per[2]
        dup = {n for n in common if not n.startswith(('header','footer','form-','location'))}
        if dup: r.add('S9-05','M', f'3안 동일 섹션 {sorted(dup)[:3]}')

    # --- S10/S11 ---
    page = (o.get('page_facts','') or '') + '\n' + '\n'.join(o.get('titles',[]))
    for f in c['in'].get('filled',[]):
        if f.get('action')=='fill':
            v = str(f.get('value',''))
            vt = tokens(v)
            if vt and not (vt <= tokens(page)):
                r.add('S10-01','C', f'유저 값 유실 의심 {f.get("step")}')
            elif not vt and v and norm(v)[:10] not in norm(page):
                r.add('S10-01','C', f'유저 값 유실 의심 {f.get("step")}')
    bad2 = [t for t in tokens(o.get('page_facts','')) - INtok - FILLEDtok if t[0] != 'url']
    if bad2: r.add('S11-05','C', f'최종 페이지 지어낸 사실 {bad2[:4]}')
    if re.search(r'label|LABEL|EYEBROW|lorem|플레이스홀더', page): r.add('S11-06','C','제작 용어 렌더')
    for t in o.get('titles',[]):
        if re.search(r'(보기|하기|받기|주세요|나요|까요|인가요)$|\?', t) or re.search(r'(것|것들|거|데|점|분들|사람)$', t):
            r.add('S11-01','M', f'타이틀 종결 「{t}」')
        if re.search(r'(는|면|에|이|가|고)$', t) and len(t)>3:
            r.add('S11-01','M', f'타이틀 조사 종결 「{t}」')
    # S11-20 주제 필수 정보 (단순판: 행사/판매/모집 핵심 토큰)
    need = {'1-①':'date','1-②':'date','1-③':'date','1-④':'time',
            '4-①':'money','4-④':'money','3-②':'money',
            '5-①':'date','5-②':'date','5-④':None,'5-⑤':'account'}
    k = need.get(g.get('topic'))
    if k:
        in_has = any(t[0]==k for t in INtok | FILLEDtok)
        page_has = any(t[0]==k for t in tokens(page))
        q_labels = ' '.join(kk.get('라벨','') for st in o.get('q',[]) for kk in st.get('칸',[]))
        if in_has and not page_has: r.add('S11-20','M', f'필수 정보({k}) IN에 있는데 페이지에 없음')
        if not in_has and not page_has and not q_labels: r.add('S11-20','m', f'필수 정보({k}) 받는 칸도 없음(샘플 한계)')
    return r.hits

def score(hits):
    C = sum(1 for h in hits if h['sev']=='C'); M = sum(1 for h in hits if h['sev']=='M'); m = sum(1 for h in hits if h['sev']=='m')
    return {'C':C,'M':M,'m':m,'score':max(0,100-4*M-1*m),'FAIL':C>0}

if __name__ == '__main__':
    idx = json.load(open(os.path.join(HERE,'..','..','..','..','1. 작업 가이드','.data','preset-index','preset-index.json')))
    INDEX_NAMES = {i['name'] for i in idx}
    globals()['INDEX_NAMES'] = INDEX_NAMES
    cases = []
    for f in sorted(glob.glob(os.path.join(HERE,'cases-*.json'))):
        cases += json.load(open(f))
    results = []
    agg = collections.Counter(); sev_by = {}
    for c in cases:
        hits = check_case(c)
        s = score(hits)
        results.append({'id':c['id'],'persona':c.get('persona'),'hits':hits, **s})
        for h in hits: agg[h['check']] += 1; sev_by[h['check']] = h['sev']
    json.dump({'n':len(cases),'results':results}, open(os.path.join(HERE,'results.json'),'w'), ensure_ascii=False, indent=1)
    print(f'케이스 {len(cases)}개 채점 완료')
    fails = [r for r in results if r['FAIL']]
    print(f'FAIL(C급) {len(fails)}건 · 통과(≥90 & C=0) {sum(1 for r in results if not r["FAIL"] and r["score"]>=90)}건 · 평균 {sum(r["score"] for r in results)/max(1,len(results)):.1f}점')
    print('\n체크별 발생 건수 (내림차순):')
    for k,v in agg.most_common():
        print(f'  {k} [{sev_by[k]}] × {v}')
