/* ============================================================================
 * CdBd 에디터 카드 자동화 드라이버 (JS, 좌표 클릭 없음)
 * ----------------------------------------------------------------------------
 * CdBd 에디터(https://www.cdbd.in/editor/{id})의 페이지 컨텍스트에 주입해서
 * 카드 추가 / 삭제 / 복제를 React fiber의 onClick 핸들러를 직접 호출하는 방식으로
 * 자동화한다. 마우스 좌표 클릭(브라우저 자동화 click)을 쓰지 않는다.
 *
 * 사용법 (gstack browse 예):
 *   $B eval card-driver.js        # window.__cdbd 설치 ('installed' 반환)
 *   $B js "window.__cdbd.count()" # 마운트된 카드 수/타입
 *   ... 아래 SKILL.md의 오케스트레이션 레시피 참고 (단계 사이 sleep 필요)
 *
 * 검증: editor 4903 에서 add(image/button)·delete·duplicate·text-duplicate 실측.
 * ========================================================================== */
(() => {
  const fiberOf = (el) => {
    const k = Object.keys(el).find((k) => k.startsWith("__reactFiber$"));
    return k ? el[k] : null;
  };

  // fiber 조상(최대 depth)에서 onClick 함수를 찾아 반환.
  // sig(정규식) 지정 시: 소스가 sig에 매칭되는 onClick만 반환(잘못된 래퍼 onClick 회피).
  const onClickOf = (el, depth = 5, sig = null) => {
    let n = fiberOf(el);
    for (let i = 0; i < depth && n; i++) {
      const p = n.memoizedProps;
      if (p && typeof p.onClick === "function") {
        if (!sig || sig.test(p.onClick.toString())) return p.onClick;
      }
      n = n.return;
    }
    return null;
  };

  // 카드 보드(우측)의 카드 행 DOM 목록. 모바일 프리뷰(좌측)는 제외.
  const boardRows = () =>
    [...document.querySelectorAll("div")].filter((el) => {
      const r = el.getBoundingClientRect();
      return (
        r.x > 540 && r.x < 880 && r.width > 280 && r.height > 40 && r.height < 90
      );
    });

  // 각 행 fiber에서 block 객체({id,type,...})를 회수
  const blockOfRow = (el) => {
    let n = fiberOf(el),
      d = 0;
    while (n && d < 3) {
      if (n.memoizedProps && n.memoizedProps.block && n.memoizedProps.block.id)
        return n.memoizedProps.block;
      n = n.return;
      d++;
    }
    return null;
  };

  // 현재 "마운트된" 카드 목록(가상화로 화면 밖 카드는 안 잡힐 수 있음 → delta 비교용)
  const blocks = () => {
    const map = new Map();
    for (const el of document.querySelectorAll("div")) {
      let n = fiberOf(el),
        d = 0;
      while (n && d < 2) {
        const b = n.memoizedProps && n.memoizedProps.block;
        if (b && b.id && b.type) map.set(b.id, b.type);
        n = n.return;
        d++;
      }
    }
    return map;
  };

  const count = () => {
    const m = blocks();
    const types = {};
    for (const t of m.values()) types[t] = (types[t] || 0) + 1;
    return { total: m.size, types };
  };

  // ── 카드 추가 ──────────────────────────────────────────────────────────
  // 1) 모달 열기
  const openAddModal = () => {
    const b = [...document.querySelectorAll("button")].find(
      (e) => e.textContent.trim() === "카드 추가하기"
    );
    if (!b) return "no-add-button(모달이 이미 열려있을 수 있음)";
    b.click();
    return "modal-opening";
  };

  // 2) 모달 안에서 카드 타입 선택 → 추가. (모달 렌더 후 호출, 단계 사이 ~1s 대기)
  //    label: '이미지' '버튼' '프로필' '갤러리' '위치' '구분선' 'SNS' '메뉴' '상품'
  //           '유튜브' 'Q&A' '예약' / 2열: '텍스트 + 텍스트' 등
  //    ⚠️ '텍스트' 단일은 포커스(선택된 카드) 의존이라 불안정 → duplicateFirst({type:'text'}) 사용 권장
  //    ⚠️ '예약'은 별도 크레딧 확인 다이얼로그가 한 번 더 뜸 (confirmReservation 참고)
  // 추가 핸들러는 모달의 "카드 항목 컴포넌트"에 달려 있다. 이 컴포넌트는
  // memoizedProps에 Icon/title/description 를 갖는다(예: {Icon,onClick,title,description}).
  // 이걸로 매칭하면 잘못된 래퍼(탭/컨테이너) onClick을 피하고, t()든 다이얼로그형(예약)이든
  // 모든 타입의 진짜 항목 핸들러를 잡는다.
  const pickCardType = (label) => {
    const items = [...document.querySelectorAll("div")].filter((el) => {
      const r = el.getBoundingClientRect();
      return (
        el.textContent.trim() === label && r.width > 120 && r.y > 0 && r.y < 760
      );
    });
    for (const it of items) {
      let n = fiberOf(it);
      for (let i = 0; i < 6 && n; i++) {
        const p = n.memoizedProps;
        if (
          p &&
          typeof p.onClick === "function" &&
          ("Icon" in p || "title" in p || "description" in p)
        ) {
          p.onClick();
          return `picked:${label}`;
        }
        n = n.return;
      }
    }
    return `not-found:${label}(모달이 열려있는지/라벨이 보이는지/단일'텍스트'는 불안정인지 확인)`;
  };

  // 예약 카드 전용: pickCardType('예약') 후 뜨는 "카드 추가하기" 확인 버튼.
  // ⚠️ 이 버튼(MuiLoadingButton)은 DB 예약레코드 생성 네트워크 요청을 띄운다 →
  //    크레딧 잔액이 충분해야 최종 추가 완료. 0-크레딧이면 로딩 상태로 멈춤(취소: '취소하기').
  const confirmReservation = () => {
    const btn = [...document.querySelectorAll("button")].find(
      (b) =>
        b.textContent.trim() === "카드 추가하기" &&
        b.className.includes("MuiButton-contained")
    );
    if (!btn) return "no-reservation-confirm";
    btn.click();
    return "reservation-confirmed";
  };

  // ── kebab(•••) 메뉴 ────────────────────────────────────────────────────
  // matcher: {type:'text'} | {id:'...'} | {index:N}  (마운트된 행 기준)
  const openKebab = (matcher = {}) => {
    const rows = boardRows();
    let target = null;
    if (matcher.index != null) {
      target = rows[matcher.index] || null;
    } else {
      for (const el of rows) {
        const b = blockOfRow(el);
        if (!b) continue;
        if (matcher.id && b.id === matcher.id) {
          target = el;
          break;
        }
        if (matcher.type && b.type === matcher.type) {
          target = el;
          break;
        }
      }
    }
    if (!target) return "no-matching-row";
    const r = target.getBoundingClientRect();
    const x = Math.round(r.right - 18),
      y = Math.round(r.top + r.height / 2);
    const btn = document.elementFromPoint(x, y) && document.elementFromPoint(x, y).closest("button");
    if (!btn) return "no-kebab-button";
    btn.click();
    return "kebab-opened";
  };

  // 메뉴 항목 클릭: '카드 삭제하기' | '카드 복제하기' | '내 카드로 저장하기'
  const menuClick = (label) => {
    const item = [...document.querySelectorAll(".MuiMenuItem-root,[role=menuitem]")].find(
      (e) => e.textContent.trim() === label
    );
    if (!item) return `no-menu-item:${label}`;
    const fn = onClickOf(item, 4);
    if (!fn) return `no-handler:${label}`;
    fn();
    return `clicked:${label}`;
  };

  // 삭제 확인 다이얼로그(SweetAlert) 확인 버튼
  const confirmSwal = () => {
    const c = document.querySelector(".swal2-confirm");
    if (!c) return "no-swal";
    c.click();
    return "swal-confirmed";
  };

  // ── 페이지 색상 (테마) ────────────────────────────────────────────────
  // swatch 클릭·SketchPicker·hex input 전부 없이, 각 색 슬롯의 React onChange("#hex")를
  // fiber로 직접 호출해 색을 설정한다. 실제 클릭 0번.

  // "색상 더보기" → "페이지 색상 선택하기" 모달 열기 (페이지 테마 패널이 열린 상태에서)
  const openColorPicker = () => {
    const el = [...document.querySelectorAll("*")].find(
      (e) => e.textContent.trim() === "색상 더보기" && e.getBoundingClientRect().width > 100
    );
    if (!el) return "no-색상더보기(페이지 테마 패널 먼저 열기)";
    el.click();
    return "picker-opening";
  };

  // 슬롯 식별 = onChange 소스 시그니처 (위치 인덱스 ❌ — 배경 행 이미지 아이콘 때문에 어긋남)
  //   배경 = base:{…background:} · 텍스트 = base:{…color:} · 버튼 = button:{…background:}
  const _colorHandler = (slotWanted) => {
    for (const el of document.querySelectorAll("div")) {
      const r = el.getBoundingClientRect();
      if (!(r.x > 560 && r.x < 860 && r.width < 60 && r.width > 20)) continue;
      let n = fiberOf(el);
      for (let i = 0; i < 5 && n; i++) {
        const mp = n.memoizedProps;
        if (
          mp &&
          typeof mp.onChange === "function" &&
          typeof mp.value === "string" &&
          mp.value[0] === "#"
        ) {
          const src = mp.onChange.toString();
          let slot = null;
          if (/button:\{/.test(src)) slot = "버튼";
          else if (/base:\{[^}]*background:/.test(src)) slot = "배경";
          else if (/base:\{[^}]*color:/.test(src)) slot = "텍스트";
          if (slot === slotWanted) return mp;
        }
        n = n.return;
      }
    }
    return null;
  };

  // 색 1개 설정. slot: '배경' | '텍스트' | '버튼', hex: "#RRGGBB"
  // ⚠️ 여러 색은 한 번에 ❌ — 한 색씩 별도 호출 + 사이 ~1.2s 대기 + 배경을 마지막에.
  //    (각 onChange가 렌더 시점 stale state를 캡처해 앞 변경을 덮어쓰므로)
  const setThemeColor = (slot, hex) => {
    const mp = _colorHandler(slot);
    if (!mp) return `slot-not-found:${slot}(픽커 열렸는지 확인)`;
    const was = mp.value;
    mp.onChange(hex);
    return `${slot}=${hex}(was ${was})`;
  };

  // 현재 3색 값 읽기 (검증용)
  const themeColors = () => ({
    배경: _colorHandler("배경") && _colorHandler("배경").value,
    텍스트: _colorHandler("텍스트") && _colorHandler("텍스트").value,
    버튼: _colorHandler("버튼") && _colorHandler("버튼").value,
  });

  // "변경사항 저장하기"(fiber onClick) → 경고 모달은 confirmThemeWarning()로 확정
  const saveTheme = () => {
    const b = [...document.querySelectorAll("button")].find(
      (b) => b.textContent.trim() === "변경사항 저장하기"
    );
    if (!b) return "no-save-btn";
    const fn = onClickOf(b, 3);
    if (!fn) return "no-save-onClick";
    fn();
    return "save-fired";
  };

  // "페이지 테마 변경하기" 경고 모달의 "변경하기" 확정
  const confirmThemeWarning = () => {
    const b = [...document.querySelectorAll("button")].find(
      (b) => b.textContent.trim() === "변경하기"
    );
    if (!b) return "no-변경하기";
    b.click();
    return "theme-confirmed";
  };

  // ── 고수준 헬퍼 (단계 사이 대기가 필요 없는 동기 조합만) ───────────────
  // 텍스트 카드 추가 = 기존 텍스트 카드 복제 (단일 '텍스트' 모달 추가는 불안정하므로)
  // 1) openKebab({type:'text'}) → (sleep) → 2) menuClick('카드 복제하기')
  // delete = openKebab(matcher) → (sleep) → menuClick('카드 삭제하기') → (sleep) → confirmSwal()
  // duplicate = openKebab(matcher) → (sleep) → menuClick('카드 복제하기')
  // 색상 = openColorPicker → (sleep) → setThemeColor('텍스트'/'버튼'/'배경' 순, 한 색씩 sleep)
  //        → saveTheme → (sleep) → confirmThemeWarning

  window.__cdbd = {
    fiberOf,
    onClickOf,
    boardRows,
    blockOfRow,
    blocks,
    count,
    openAddModal,
    pickCardType,
    confirmReservation,
    openKebab,
    menuClick,
    confirmSwal,
    openColorPicker,
    setThemeColor,
    themeColors,
    saveTheme,
    confirmThemeWarning,
  };
  return "installed";
})();
