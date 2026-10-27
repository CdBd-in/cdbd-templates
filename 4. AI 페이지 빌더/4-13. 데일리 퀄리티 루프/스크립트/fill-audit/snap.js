// 내용 채우기 한 단계의 「왼쪽 입력 ↔ 오른쪽 미리보기」를 한 번에 떠낸다 (S12 채점 입력)
// 반환 = JSON 1줄. 브라우저에서 읽기만 하며 아무것도 바꾸지 않는다.
// 셀렉터 출처: s2js.sh 의 fieldinfo()/btns() (라이브 검증본) + 좌우 분할 기하 판정
(() => {
  const txt = (e) => (e ? (e.innerText || '').replace(/\s+/g, ' ').trim() : '');
  const vw = window.innerWidth;

  // ── 1) 오른쪽 미리보기 패널 찾기 ────────────────────────────────
  // 빌더 화면 = [왼쪽 질문/입력] [가운데 ‹ ›] [오른쪽 폰 미리보기]
  // 폰 미리보기 = 화면 오른쪽 절반에 있는 "세로로 긴" 박스 중 가장 큰 것
  const panels = [...document.querySelectorAll('div,section,main,aside')]
    .map((e) => ({ e, r: e.getBoundingClientRect() }))
    .filter(({ r }) => r.width > 180 && r.width < 760 && r.height > 260 &&
                       r.left > vw * 0.45 && r.height > r.width);
  panels.sort((a, b) => (b.r.width * b.r.height) - (a.r.width * a.r.height));
  const pv = panels[0] ? panels[0].e : null;

  // ── 2) 왼쪽 입력 영역 = 미리보기 바깥 ──────────────────────────
  const inPreview = (el) => !!(pv && pv.contains(el));

  // 활성(지금 묻는) 칸 — s2js.sh fieldinfo() 와 같은 규칙
  const labelOf = (t) => {
    let lb = '';
    const l = t.closest('label');
    if (l && l.querySelector('span')) lb = txt(l.querySelector('span'));
    if (!lb) lb = t.getAttribute('aria-label') || '';
    if (!lb) {
      let p = t;
      for (let k = 0; k < 3 && p; k++) {
        p = p.parentElement;
        const s = p && p.querySelector('span');
        const tx = txt(s);
        if (tx && tx.length <= 20) { lb = tx; break; }
      }
    }
    return lb;
  };

  const fields = [...document.querySelectorAll('textarea,input:not([type=file])')]
    .filter((t) => t.offsetParent && !t.readOnly && !inPreview(t))
    .map((t) => {
      const r = t.getBoundingClientRect();
      return {
        label: labelOf(t),
        value: (t.value || '').trim(),
        placeholder: (t.placeholder || '').trim(),
        filled: !!(t.value || '').trim(),
        y: Math.round(r.top),
      };
    });

  // 이미지 업로드 자리
  const hasDrop = /이 곳을 클릭하거나/.test(document.body.innerText) &&
                  !!document.querySelector('input[type=file]');

  // 접힌(이미 답한) 칸 — 체크 아이콘 줄의 라벨/값 · 「추가하기」 = 건너뛴 칸
  const chips = [...document.querySelectorAll('div,li')]
    .filter((e) => !inPreview(e) && e.children.length <= 4 && e.getBoundingClientRect().width > 120)
    .map((e) => txt(e))
    .filter((t) => t && t.length <= 60);

  // ── 3) 미리보기 텍스트 (렌더 순서대로) ─────────────────────────
  let preview = [];
  if (pv) {
    preview = [...pv.querySelectorAll('*')]
      .filter((e) => !e.children.length)
      .map((e) => {
        const r = e.getBoundingClientRect();
        const st = getComputedStyle(e);
        return {
          t: txt(e),
          y: Math.round(r.top),
          x: Math.round(r.left),
          cx: Math.round(r.left + r.width / 2),   // 정렬 비교용 중심 x (S12-06)
          w: Math.round(r.width),
          h: Math.round(r.height),
          lh: Math.round(parseFloat(st.lineHeight) || parseFloat(st.fontSize) * 1.5 || 0),
          align: st.textAlign,
          // 흐린 견본인지 진한 본문인지 — 색 불투명도로 가른다
          op: Number(st.opacity),
          color: st.color,
        };
      })
      .filter((o) => o.t && o.t.length <= 200)
      .sort((a, b) => (a.y - b.y) || (a.x - b.x));
  }

  // ── 3-B) 미리보기 안 이미지·면의 모서리 (S12-08) ───────────────
  // 풀블리드(패널 폭에 꽉 찬) 박스는 모서리 0이 정상이라 따로 표시해 둔다
  let shapes = [];
  if (pv) {
    const pw = pv.getBoundingClientRect().width;
    shapes = [...pv.querySelectorAll('img,[style*="background-image"]')]
      .map((e) => {
        const r = e.getBoundingClientRect();
        const st = getComputedStyle(e);
        return {
          r: Math.round(parseFloat(st.borderRadius) || 0),
          w: Math.round(r.width),
          y: Math.round(r.top),
          full: r.width >= pw - 2,
        };
      })
      .filter((o) => o.w > 40);
  }

  // ── 3-C) 입력칸이 딸리지 않은 라벨 (S12-12) ───────────────────
  // 왼쪽 영역의 라벨 글자 중, 어떤 입력칸의 라벨로도 잡히지 않은 것
  const fieldLabels = new Set(fields.map((f) => f.label).filter(Boolean));
  const orphanLabels = [...document.querySelectorAll('label')]
    .filter((l) => !inPreview(l) && l.offsetParent)
    .filter((l) => !l.querySelector('input,textarea,select'))
    .map((l) => txt(l))
    .filter((t) => t && t.length <= 12 && !fieldLabels.has(t));

  // ── 4) 하단 진행 버튼 ──────────────────────────────────────────
  const btn = [...document.querySelectorAll('button')]
    .filter((b) => !inPreview(b) && b.offsetParent)
    .map((b) => txt(b))
    .find((t) => t === '다음' || t === '이건 없어요') || '';

  return JSON.stringify({
    heading: txt(document.querySelector('h1,h2')) ||
             document.body.innerText.replace(/\s+/g, ' ').slice(0, 90),
    fields: fields.sort((a, b) => a.y - b.y),
    hasImageDrop: hasDrop,
    chips: [...new Set(chips)].slice(0, 40),
    button: btn,
    preview,
    shapes,
    orphanLabels: [...new Set(orphanLabels)],
    previewFound: !!pv,
    previewWidth: pv ? Math.round(pv.getBoundingClientRect().width) : 0,
    previewBg: (() => {            // 견본/본문 판정은 배경 대비로 한다(다크 테마 대응)
      let e = pv;
      while (e) {
        const c = getComputedStyle(e).backgroundColor;
        if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) return c;
        e = e.parentElement;
      }
      return 'rgb(255,255,255)';
    })(),
  });
})()
