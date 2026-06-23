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
  // 추가 핸들러 시그니처: t({...}) / t(builder(...)) / n((0,..insert..)) / 메뉴 a((0,..))
  // 잘못된 래퍼(예: 탭/컨테이너) onClick을 피하려고 소스로 매칭한다.
  const ADD_SIG = /(\bt\(|\bn\(\(0,|\ba\(\(0,)/;
  const pickCardType = (label) => {
    const items = [...document.querySelectorAll("div")].filter((el) => {
      const r = el.getBoundingClientRect();
      return (
        el.textContent.trim() === label && r.width > 120 && r.y > 0 && r.y < 760
      );
    });
    for (const it of items) {
      const fn = onClickOf(it, 5, ADD_SIG);
      if (fn) {
        fn();
        return `picked:${label}`;
      }
    }
    return `not-found:${label}(모달이 열려있는지/라벨이 보이는지/단일'텍스트'는 불안정인지 확인)`;
  };

  // 예약 카드 전용: pickCardType('예약') 후 뜨는 "카드 추가하기" 확인 버튼
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

  // ── 고수준 헬퍼 (단계 사이 대기가 필요 없는 동기 조합만) ───────────────
  // 텍스트 카드 추가 = 기존 텍스트 카드 복제 (단일 '텍스트' 모달 추가는 불안정하므로)
  // 1) openKebab({type:'text'}) → (sleep) → 2) menuClick('카드 복제하기')
  // delete = openKebab(matcher) → (sleep) → menuClick('카드 삭제하기') → (sleep) → confirmSwal()
  // duplicate = openKebab(matcher) → (sleep) → menuClick('카드 복제하기')

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
  };
  return "installed";
})();
