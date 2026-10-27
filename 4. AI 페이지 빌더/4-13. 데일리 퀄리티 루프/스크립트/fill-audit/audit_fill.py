#!/usr/bin/env python3
# S12 채점 — 「내용 채우기」 단계 덤프(snap.js 산출 JSONL)를 읽어 입력 ↔ 미리보기를 대조한다.
# 사용: audit_fill.py <사례ID>-fill.jsonl   (한 줄 = 한 단계)
# 기준 정본 = 4-9-5 S12 · 판정식만 구현하고 주관 판단은 하지 않는다.
import json, re, sys
from collections import Counter

LINK_PAT = re.compile(
    r'\d{2,4}-\d{3,4}-\d{4}|https?://|www\.|@[\w.-]+\.(?:com|net|kr)|pf\.kakao\.com')
SENT_END = re.compile(r'(해 주세요|하세요|합니다|해주세요)$')
FIELD_BAD_LABEL = re.compile(r'^(값|유형|타입|항목값)$|( 값| 라벨)$')


def norm(s):
    return re.sub(r'\s+', '', s or '')


def load(path):
    steps = []
    for ln in open(path, encoding='utf-8'):
        ln = ln.strip()
        if ln:
            steps.append(json.loads(ln))
    return steps


def is_periodic(labs, min_period=1):
    """라벨 배열이 길이 k 묶음의 되풀이인가 — 반복 항목 판정
    k=1(같은 라벨만 N개)도 반복으로 본다. 단 그 라벨이 「한 섹션에 하나뿐이어야 하는
    본문류」면 호출부에서 따로 거른다(섹션 원본 통합 대상 신호)."""
    n = len(labs)
    if n < min_period * 2:
        return False
    for k in range(min_period, n // 2 + 1):
        if n % k:
            continue
        if all(labs[j] == labs[j % k] for j in range(n)):
            return True
    return False


# 반복 항목으로 여러 벌 나오는 게 정상인 라벨 (버튼·연락처·항목 등)
REPEATABLE = re.compile(r'버튼|연락처|문구|항목|제품|이미지|사진|질문|답변|회차|메뉴')
# 한 섹션에 하나뿐이어야 하는 본문류 — 2개 이상이면 섹션 원본 통합 대상
SINGULAR = re.compile(r'^(본문 텍스트|소개 문구|설명 문구|본문|설명)$')
# S12-14 — 전 행이 같은 글리프인 구분점·체크 표식 (뜻 있는 이모지와 구분)
MARKER_GLYPHS = {'●', '•', '·', '○', '■', '▪', '◆', '✓', '✔', '✔️', '✅', '☑', '☑️',
                 '-', '—', '–', '*', '▶', '▸', '→'}


def lum(color):
    """css 색 → 명도 0~1 (파싱 실패 시 None)"""
    m = re.match(r'rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)', color or '')
    if not m:
        return None
    r, g, b = (float(m.group(i)) / 255 for i in (1, 2, 3))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def faint(p, bg=None):
    """미리보기 항목이 흐린 견본인지 — 불투명도 ＋ 배경 대비로 판정.
    🔑 절대 색으로 「밝은 회색 = 견본」이라 보면 다크 테마의 흰 본문을 견본으로 오판한다
       (2026-10-27 실측 — 그 탓에 다크 페이지에서 S12 전 체크가 무력화됐다)."""
    if p.get('op') is not None and p['op'] < 0.75:
        return True
    m = re.match(r'rgba?\([\d.]+,\s*[\d.]+,\s*[\d.]+,\s*([\d.]+)\)', p.get('color', ''))
    if m and float(m.group(1)) < 0.75:
        return True
    fg = lum(p.get('color', ''))
    bgl = lum(bg) if bg else None
    if fg is not None and bgl is not None:
        return abs(fg - bgl) < 0.35        # 배경과 가까운 글자 = 흐린 견본
    return False


def audit(steps):
    out = []          # (체크ID, 단계번호, 메시지)
    seen_sig = {}

    for i, s in enumerate(steps, 1):
        head = s.get('heading', '')[:40]
        fields = s.get('fields', [])
        pv = s.get('preview', [])
        bg = s.get('previewBg')
        pv_solid = [p for p in pv if not faint(p, bg)]
        pv_text = {norm(p['t']) for p in pv_solid}

        # ── S12-05 / S5-28 단계 중복 0 ───────────────────────────
        sig = (norm(head), tuple(norm(f['label']) for f in fields))
        if sig in seen_sig:
            out.append(('S12-05', i, f'단계 중복 — {head!r} 가 {seen_sig[sig]}단계와 같은 칸 구성'))
        else:
            seen_sig[sig] = i

        # ── S12-01 빈 입력 ↔ 채워진 미리보기 ─────────────────────
        # 미리보기는 한 칸의 글이 여러 줄로 쪼개져 렌더될 수 있다(제목＋설명 두 줄 등)
        # → 완전 일치 ＋ 「조각이 칸 글 안에 들어가는지」 부분 매칭 둘 다 본다
        for f in fields:
            if f['filled']:
                continue
            ph = norm(re.sub(r'^예:\s*', '', f.get('placeholder', '')))
            if not ph:
                continue
            hit = None
            if ph in pv_text:
                hit = ph
            else:
                for p in pv_solid:
                    frag = norm(p['t'])
                    if len(frag) >= 6 and frag in ph:
                        hit = frag
                        break
            if hit:
                out.append(('S12-01', i,
                            f'빈 칸 {f["label"]!r} 인데 미리보기에 그 글이 진하게 렌더 — {hit[:30]!r}'))

        # ── S5-29 하단 버튼 문구 = 칸 상태 ───────────────────────
        # hasImageDrop = 업로드 드롭존이 보인다 = 그 이미지 칸은 「비어 있음」
        btn = s.get('button', '')
        all_empty = (not any(f['filled'] for f in fields)) and (fields or s.get('hasImageDrop'))
        if btn == '다음' and all_empty:
            out.append(('S5-29', i, f'칸이 전부 빈 화면인데 버튼이 「다음」 — {head!r}'))
        if btn == '이건 없어요' and fields and all(f['filled'] for f in fields):
            out.append(('S5-29', i, f'칸이 전부 찼는데 버튼이 「이건 없어요」 — {head!r}'))

        # ── S5-05 국문 내부 필드명 · S5-02 동일 라벨 ─────────────
        labs = [f['label'] for f in fields if f['label']]
        for lb in labs:
            if FIELD_BAD_LABEL.search(lb.strip()):
                out.append(('S5-05', i, f'내부 필드명이 칸 라벨로 노출 — {lb!r}'))
        # 반복 묶음이면 라벨이 주기적으로 되풀이된다([버튼 문구, 연락처] × N) → 정상
        # 반복이 자연스러운 라벨(버튼·연락처·항목…)은 같은 라벨만 N개여도 정상
        periodic2 = is_periodic(labs, min_period=2)
        # 「X 추가」 버튼이 있으면 그 X 는 반복 묶음의 칸이다 — 같은 라벨이 N개여도 정상
        add_nouns = {norm(a.get('t', '')).replace('추가하기', '').replace('추가', '').strip()
                     for a in (s.get('addButtons') or [])}
        add_nouns.discard('')
        for lb, n in Counter(labs).items():
            if n < 2:
                continue
            if SINGULAR.match(lb.strip()):
                out.append(('S5-02', i,
                            f'같은 라벨 {n}회 — {lb!r} (한 섹션에 하나뿐이어야 하는 본문 칸 '
                            f'· 섹션 원본 통합 대상)'))
            elif not periodic2 and not REPEATABLE.search(lb) and norm(lb) not in add_nouns:
                out.append(('S5-02', i,
                            f'같은 라벨 {n}회 — {lb!r} (반복으로 안 묶였거나 구분어 필요)'))

        # ── S6-15 버튼 보이는 글자 = 행동어 ──────────────────────
        for f in fields:
            lb = f['label']
            if not re.search(r'버튼|문구|이름|채널', lb or ''):
                continue
            v = f['value']
            if v and (LINK_PAT.search(v) or SENT_END.search(v)):
                out.append(('S6-15', i, f'보이는 글자 칸 {lb!r} 에 링크값·문장 — {v[:30]!r}'))

        # ── S5-27 연락·채널 버튼 = 두 칸 쌍 ──────────────────────
        link_fields = [f for f in fields if f['value'] and LINK_PAT.search(f['value'])]
        if link_fields and not any(re.search(r'버튼|문구|이름', f['label'] or '') for f in fields):
            out.append(('S5-27', i,
                        f'연결 값 칸만 있고 「버튼 문구」 칸이 없음 — {head!r} '
                        f'({link_fields[0]["value"][:24]!r})'))

        # ── S12-02 한 값 두 자리 (단계 안) ───────────────────────
        for f in fields:
            if not f['filled']:
                continue
            same = [p for p in pv_solid if norm(p['t']) == norm(f['value'])]
            if len(same) >= 2:
                out.append(('S12-02', i, f'같은 값이 미리보기 두 자리에 — {f["value"][:24]!r}'))

        # ── S12-09 좁은 열에서 글이 과하게 접힘 ──────────────────
        # 다단(2~4열) 칸에 긴 글이 들어가면 두세 글자마다 줄이 꺾인다 → 그 섹션은 그 내용에 안 맞다
        pw = s.get('previewWidth') or 0
        if pw:
            for p in pv_solid:
                w, h, lh = p.get('w') or 0, p.get('h') or 0, p.get('lh') or 0
                if not (w and h and lh):
                    continue
                lines = round(h / lh) if lh else 1
                narrow = w < pw / 2.4            # 2열 이상으로 쪼개진 칸
                if narrow and lines >= 4 and len(p['t']) >= 20:
                    out.append(('S12-09', i,
                                f'좁은 칸({w}px)에 긴 글이 {lines}줄로 접힘 — {p["t"][:24]!r} '
                                f'· 다단 말고 세로 스택·전폭 행으로'))
                    break

        # ── S6-16 값 칸에 아이콘 글리프·슬롯 견본 라벨 ───────────
        for f in fields:
            v = f.get('value') or ''
            if not v:
                continue
            if re.match(r'^[\U0001F300-\U0001FAFF☀-➿]\s*', v):
                out.append(('S6-16', i,
                            f'값 칸 {f["label"]!r} 맨 앞에 아이콘 글자 — {v[:24]!r} '
                            f'(아이콘은 고른 유형을 따라 자동으로 붙는다)'))
            elif re.match(r'^(CALL|HOMEPAGE|EMAIL|MESSAGE|HOME|SNS|TEL)\W*\S', v, re.I):
                out.append(('S6-16', i,
                            f'값 칸 {f["label"]!r} 에 섹션 원본의 견본 라벨이 붙음 — {v[:24]!r}'))

        # ── S12-10 반복 항목 간 시각 표현 동일 ──────────────────
        # 같은 값이 반복 목록으로 들어간 항목들의 「제목 조각 상대 위치」를 비교한다.
        # 항목 경계 = 입력의 반복 벌(같은 라벨 주기) · 미리보기에선 같은 라벨 값들의 y 순서
        rep_vals = [f['value'] for f in fields if f['filled'] and len(f['value']) <= 30]
        anchors = []
        for v in rep_vals:
            hit = next((p for p in pv_solid if norm(p['t']) == norm(v)), None)
            if hit and hit.get('cx') is not None:
                anchors.append((v, hit))
        # ⚠️ 2항목만으로는 「교대 설계」와 「불일치」를 가를 수 없다(지그재그 2열 원본이 실재)
        #    → 3항목 이상일 때만 판정하고, 2항목은 S12-04(원본 대조)에 맡긴다
        if len(anchors) >= 3 and pw:
            # 같은 역할 값들의 가로 위치가 제각각이면(좌/중/우가 섞이면) 표현 불일치
            zones = []
            for v, h in anchors:
                z = 'L' if h['cx'] < pw * 0.4 else ('R' if h['cx'] > pw * 0.6 else 'C')
                zones.append(z)
            uniq = set(zones)
            # 규칙적 교대(LRLR…)는 원본 설계이므로 통과
            alternating = all(zones[k] != zones[k + 1] for k in range(len(zones) - 1)) and len(uniq) == 2
            if len(uniq) >= 2 and not alternating:
                out.append(('S12-10', i,
                            f'같은 역할 값들의 가로 위치가 제각각 — {"".join(zones)} '
                            f'({[v[:10] for v, _ in anchors][:4]}) · 항목마다 같은 자리에'))

        # ── S12-11 미리보기에 시간 「범위」인데 입력은 시작만 ────
        TIME_RANGE = re.compile(r'(\d{1,2}:\d{2})\s*[~\-–]\s*(\d{1,2}:\d{2})')
        rng = next((TIME_RANGE.search(p['t']) for p in pv_solid if TIME_RANGE.search(p['t'])), None)
        if rng:
            time_fields = [f for f in fields if re.search(r'시간|시각', f.get('label') or '')]
            vals = {norm(f.get('value') or '') for f in time_fields if f.get('value')}
            if len(time_fields) <= 1 or norm(rng.group(2)) not in vals:
                out.append(('S12-11', i,
                            f'미리보기엔 시간 범위 {rng.group(0)!r} 인데 입력엔 종료 시각 칸이 없음'
                            f'(시간 칸 {len(time_fields)}개) — 「종료일 추가」를 켜고 채울 것'))
            # 시작 시각이 미리보기와 다르면 사실 오류
            for f in time_fields:
                v = norm(f.get('value') or '')
                if v and v not in (norm(rng.group(1)), norm(rng.group(2))):
                    out.append(('S6-02', i,
                                f'시작 시각이 미리보기와 다름 — 입력 {f["value"]!r} vs 미리보기 {rng.group(1)!r}'))

        # ── S12-12 입력칸 없는 라벨 (묶음 라벨＋칸 라벨 중복) ────
        for lb in s.get('orphanLabels') or []:
            out.append(('S12-12', i,
                        f'입력칸이 딸리지 않은 라벨 — {lb!r} '
                        f'(묶음 라벨은 칸 라벨을 생략할 때만 · 둘 다 ❌)'))

        # ── S12-13 대표 칸(접힌 항목 요약) = 「제목」 칸 ─────────
        # 규칙(MD-09-1 3-2 🏷) = ① 라벨 `제목` 칸이 있으면 그것 ② 2단이면 안쪽 반복 칸 ❌
        chips = [c for c in (s.get('chips') or []) if c]
        title_f = next((f for f in fields
                        if norm(f.get('label')) == '제목' and f.get('filled')), None)
        if title_f and chips:
            others = {norm(f['value']): f['label'] for f in fields
                      if f.get('filled') and norm(f.get('label')) != '제목'}
            for c in chips:
                nc = norm(c)
                if nc in others and norm(title_f['value']) not in nc:
                    out.append(('S12-13', i,
                                f'접힌 항목 요약이 {others[nc]!r} 칸 값({c[:14]!r}) — '
                                f'「제목」 칸({title_f["value"][:14]!r})이 대표 칸이어야 한다'))
                    break

        # ── S12-07 빈 줄 문단 보존 ───────────────────────────────
        # 입력에 빈 줄이 있으면 미리보기에서도 문단이 떨어져야 한다.
        # 판정 = 두 문단 첫 조각의 y 간격이 「본문 한 줄 간격」과 같으면 빈 줄이 사라진 것
        for f in fields:
            if '\n\n' not in (f.get('value') or ''):
                continue
            paras = [p.strip() for p in f['value'].split('\n\n') if p.strip()]
            ys = []
            for para in paras:
                head = norm(para)[:14]          # 공백 제거 후 자른다(양쪽 같은 기준)
                hit = next((p for p in pv_solid if head and norm(p['t'])[:14] == head), None)
                if hit:
                    ys.append(hit['y'])
            if len(ys) >= 2:
                gaps = [b - a for a, b in zip(ys, ys[1:])]
                # 같은 문단 안 줄 간격 추정 = 미리보기 조각들의 최빈 간격
                line_gaps = [b['y'] - a['y'] for a, b in zip(pv_solid, pv_solid[1:])
                             if 0 < b['y'] - a['y'] < 80]
                base = min(line_gaps) if line_gaps else 0
                if base and any(g <= base * 1.4 for g in gaps):
                    out.append(('S12-07', i,
                                f'빈 줄 문단이 미리보기에서 붙음 — 칸 {f["label"]!r} '
                                f'(문단 간격 {gaps} vs 줄 간격 {base})'))

        # ── S12-06 타이틀 ↔ 본문 첫 카드 정렬 통일 ───────────────
        # 미리보기 맨 위 짧은 글(섹션 타이틀)과 그 아래 첫 본문(20자↑)의 중심 x 비교
        if len(pv_solid) >= 2:
            title = next((p for p in pv_solid if 0 < len(p['t']) <= 14), None)
            if title:
                body_p = next((p for p in pv_solid
                               if p['y'] > title['y'] and len(p['t']) >= 20), None)
                if body_p and title.get('cx') is not None and body_p.get('cx') is not None:
                    width = s.get('previewWidth') or 0
                    if width and abs(title['cx'] - body_p['cx']) > width * 0.08:
                        out.append(('S12-06', i,
                                    f'타이틀 {title["t"][:12]!r} 과 본문의 정렬이 다름 '
                                    f'(중심 x {title["cx"]} vs {body_p["cx"]})'))

        # ── S12-03 칸 순서 = 미리보기 순서 ───────────────────────
        pos = []
        for f in fields:
            if not f['filled']:
                continue
            hit = next((k for k, p in enumerate(pv_solid) if norm(p['t']) == norm(f['value'])), None)
            if hit is not None:
                pos.append((f['label'], hit))
        if len(pos) >= 2 and [p for _, p in pos] != sorted(p for _, p in pos):
            out.append(('S12-03', i,
                        '입력 칸 순서 ≠ 미리보기 순서 — 입력 '
                        + ' → '.join(l for l, _ in pos)))

    # ── S12-14 구분점 글리프가 입력 값으로 ────────────────────────
    # 뜻 있는 이모지(🧘·⏰)는 칸을 주는 게 맞지만(MD-09-1), 전 행이 같은 구분점(●·✓)은 장식이다
    for i, st in enumerate(steps, 1):
        hits = []
        for f in st.get('fields') or []:
            v = norm(f.get('value'))
            if v and all(ch in MARKER_GLYPHS or ch.isspace() for ch in v):
                hits.append(f'{f.get("label") or "칸"}=“{v}”')
        for c in st.get('chips') or []:
            v = norm(c)
            if v and all(ch in MARKER_GLYPHS or ch.isspace() for ch in v):
                hits.append(f'접힌 항목 이름=“{v}”')
        if hits:
            out.append(('S12-14', i, '구분점 글리프가 입력 값으로 들어감 — ' + ' / '.join(dict.fromkeys(hits))[:160]
                        + ' · 전 행이 같은 표식이면 장식이라 입력칸을 주지 않는다'))

    # ── S12-15 「추가」 액션이 여러 곳 (껍데기뿐인 바깥 묶음) ───────
    # 2단 반복인데 바깥 묶음에 자기 칸이 없으면 바깥은 껍데기 — 1단이어야 한다
    for i, st in enumerate(steps, 1):
        adds = st.get('addButtons') or []
        if len(adds) < 2:
            continue
        inner = adds[0]
        noun = norm(inner['t']).replace('추가하기', '').replace('추가', '').strip()
        own = [f for f in (st.get('fields') or [])
               if f.get('y', 10 ** 6) < inner.get('y', 0) and norm(f.get('label')) not in ('', noun)]
        if not own:
            out.append(('S12-15', i,
                        f'「추가」 액션이 {len(adds)}곳({" · ".join(a["t"] for a in adds)}) — '
                        f'바깥 묶음에 자기 칸이 없다(안쪽 「{noun}」 칸뿐) → 2단이 아니라 1단 반복으로'))

    # ── S12-08 이미지 모서리 계열 1종 (단계 전체 = 문서 전체) ────
    # 멀티페이지는 장마다 단계가 나뉘므로 「전 단계를 모아」 봐야 장 사이 혼재가 잡힌다
    allshapes = []
    for i, s in enumerate(steps, 1):
        for sh in s.get('shapes') or []:
            if sh.get('full'):
                continue          # 풀블리드 박스는 모서리 0이 정상
            allshapes.append((i, '둥근' if sh['r'] > 0 else '각진', sh['r']))
    if allshapes:
        kinds = Counter(k for _, k, _ in allshapes)
        if len(kinds) >= 2:
            minor = kinds.most_common()[-1][0]
            major = kinds.most_common()[0][0]
            where = sorted({i for i, k, _ in allshapes if k == minor})
            out.append(('S12-08', where[0],
                        f'이미지 모서리 혼재 — {minor} {kinds[minor]}곳(단계 {where[:6]}) vs '
                        f'{major} {kinds[major]}곳 · 멀티면 전 장을 한 값으로'))

    return out


def main():
    if len(sys.argv) < 2:
        sys.exit('사용: audit_fill.py <사례ID>-fill.jsonl')
    steps = load(sys.argv[1])
    res = audit(steps)
    print(f'내용 채우기 {len(steps)}단계 검사 — 문제 {len(res)}건')
    for cid, i, msg in res:
        print(f'  [{cid}] {i}단계 · {msg}')
    # 미리보기를 못 찾은 단계가 있으면 미측정으로 알린다(조용한 통과 방지)
    miss = [i for i, s in enumerate(steps, 1) if not s.get('previewFound')]
    if miss:
        print(f'  ⚠️ 미리보기 패널 미검출 {len(miss)}단계({miss[:8]}) — S12-01~03 미측정')
    return 1 if res else 0


if __name__ == '__main__':
    sys.exit(main())
