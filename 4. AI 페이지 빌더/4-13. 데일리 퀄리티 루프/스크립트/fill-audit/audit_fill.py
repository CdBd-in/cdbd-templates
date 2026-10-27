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


def is_periodic(labs, min_period=2):
    """라벨 배열이 길이 k(≥min_period) 묶음의 되풀이인가 — 반복 항목 판정"""
    n = len(labs)
    if n < min_period * 2:
        return False
    for k in range(min_period, n // 2 + 1):
        if n % k:
            continue
        if all(labs[j] == labs[j % k] for j in range(n)):
            return True
    return False


def faint(p):
    """미리보기 항목이 흐린 견본인지 — 불투명도 또는 회색 계열로 판정"""
    if p.get('op') is not None and p['op'] < 0.75:
        return True
    m = re.match(r'rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)', p.get('color', ''))
    if m:
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        a = float(m.group(4)) if m.group(4) else 1.0
        if a < 0.75:
            return True
        # 밝은 회색 = 견본 표시
        if abs(r - g) < 12 and abs(g - b) < 12 and min(r, g, b) > 150:
            return True
    return False


def audit(steps):
    out = []          # (체크ID, 단계번호, 메시지)
    seen_sig = {}

    for i, s in enumerate(steps, 1):
        head = s.get('heading', '')[:40]
        fields = s.get('fields', [])
        pv = s.get('preview', [])
        pv_solid = [p for p in pv if not faint(p)]
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
        # 주기 ≥2 로 딱 떨어지면 통과 · 주기 1(같은 라벨만 연속)·불규칙이면 신호
        if not is_periodic(labs, min_period=2):
            for lb, n in Counter(labs).items():
                if n >= 2:
                    out.append(('S5-02', i,
                                f'같은 라벨 {n}회 — {lb!r} '
                                f'(반복으로 안 묶였거나 섹션 원본 통합 대상)'))

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
