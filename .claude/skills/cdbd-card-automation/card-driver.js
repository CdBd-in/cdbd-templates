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

  // ── 카드 고정 (핀) ────────────────────────────────────────────────────
  // 핀 버튼은 드래그 핸들 옆. ⚠️ 고정된 카드는 드래그 핸들이 사라져 핀이 왼쪽으로
  // 이동하므로 위치(x)로 찾으면 안 됨 → onClick 소스 시그니처로 식별.
  //   미고정 핀 클릭 = K(e.currentTarget) → "상단/하단에 고정하기" 메뉴
  //   고정 핀 클릭 = unpin 확인(SweetAlert) → ep(...,null)
  const _pinButton = (matcher = {}) => {
    const rows = boardRows();
    let row = null;
    if (matcher.index != null) row = rows[matcher.index];
    else {
      for (const el of rows) {
        const b = blockOfRow(el);
        if (!b) continue;
        if (matcher.id && b.id === matcher.id) { row = el; break; }
        if (matcher.type && b.type === matcher.type) { row = el; break; }
      }
    }
    if (!row) return null;
    // 현재 고정 여부는 핸들러 소스로 알 수 없음(소스엔 항상 unpinTitle 포함) →
    // block.fixedPosition(top/bottom/null)으로 판별.
    const blk = blockOfRow(row);
    const pinned = !!(blk && blk.fixedPosition);
    for (const b of row.querySelectorAll("button")) {
      let n = fiberOf(b);
      for (let i = 0; i < 3 && n; i++) {
        const p = n.memoizedProps;
        if (p && typeof p.onClick === "function") {
          const s = p.onClick.toString();
          if (/unpinTitle|K\(e\.currentTarget\)/.test(s))
            return { btn: b, fn: p.onClick, pinned, fixedPosition: blk && blk.fixedPosition };
        }
        n = n.return;
      }
    }
    return null;
  };

  // 핀 버튼 클릭. 미고정 → 위치 메뉴 열림(다음 pinTo) / 고정 → unpin 확인창(다음 confirmSwal)
  const openPin = (matcher = {}) => {
    const pb = _pinButton(matcher);
    if (!pb) return "no-pin-button";
    pb.fn({ stopPropagation: () => {}, preventDefault: () => {}, currentTarget: pb.btn });
    return pb.pinned ? "unpin-confirm-opened" : "pin-menu-opened";
  };

  // 위치 메뉴에서 고정 위치 선택. position: 'top'(상단) | 'bottom'(하단)
  const pinTo = (position = "top") => {
    const label = position === "bottom" ? "하단에 고정하기" : "상단에 고정하기";
    const it = [...document.querySelectorAll(".MuiMenuItem-root,[role=menuitem],li")].find(
      (e) => e.textContent.trim() === label
    );
    if (!it) return `no-menu-item:${label}`;
    const fn = onClickOf(it, 4);
    if (!fn) return `no-handler:${label}`;
    fn({ stopPropagation: () => {}, preventDefault: () => {} });
    return `pinned:${position}`;
  };
  // 고정: openPin(matcher) → (sleep) → pinTo('top'/'bottom')
  // 해제: openPin(matcher) → (sleep) → confirmSwal()

  // ── 이미지 업로드/적용 (React onDrop·onClick 직접 호출) ────────────────
  // CdBd 업로드는 transient <input type=file>(동적 생성·제거) → $B upload/setInputFiles ❌,
  // 실제 클릭은 OS 파일 다이얼로그 timeout. 해결: react-dropzone의 onDrop을 직접 호출.
  // 흐름: openImageUpload → uploadImage(파일은 window.__cdbdImg base64) → applyImage.

  // N번째 이미지 카드의 "이미지 업로드하기" 트리거 클릭 → "이미지 추가하기" 라이브러리 모달
  const openImageUpload = (index = 0) => {
    const b = [...document.querySelectorAll("button")].filter(
      (e) => e.textContent.trim() === "이미지 업로드하기"
    )[index];
    if (!b) return `no-trigger[${index}]`;
    const fn = onClickOf(b, 3);
    if (!fn) return "no-trigger-onClick";
    fn();
    return "upload-modal-opening";
  };

  // 라이브러리 모달의 dropzone에 파일 주입(onDrop 직접 호출).
  // 사전: window.__cdbdImg = "<base64>" (Bash: base64 -i img.png), mime/filename 인자.
  const uploadImage = (filename, mime = "image/png") => {
    if (!window.__cdbdImg) return "no-window.__cdbdImg(base64 먼저 주입)";
    const bin = atob(window.__cdbdImg);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    const file = new File([new Blob([bytes], { type: mime })], filename, { type: mime });
    const propsOf = (el) => {
      const k = Object.keys(el).find((k) => k.startsWith("__reactProps"));
      return k ? el[k] : null;
    };
    const dz = [...document.querySelectorAll("*")].find((el) => {
      const p = propsOf(el);
      return p && typeof p.onDrop === "function";
    });
    if (!dz) return "no-dropzone(라이브러리 모달 열렸는지 확인)";
    const dt = new DataTransfer();
    dt.items.add(file);
    propsOf(dz).onDrop({
      preventDefault: () => {},
      stopPropagation: () => {},
      dataTransfer: dt,
      target: dz,
      currentTarget: dz,
    });
    return `onDrop:${filename}`;
  };

  // 라이브러리에서 filename(alt/src 부분일치) 이미지 선택 → 그 셀의 "적용하기" 클릭.
  // ⚠️ "적용하기"는 모든 이미지 셀에 있으므로 반드시 해당 이미지 셀 범위 안에서 찾는다.
  const applyImage = (filenameMatch) => {
    const propsOf = (el) => {
      const k = Object.keys(el).find((k) => k.startsWith("__reactProps"));
      return k ? el[k] : null;
    };
    const img = [...document.querySelectorAll("img")].find((i) =>
      new RegExp(filenameMatch).test(i.alt || i.src)
    );
    if (!img) return `no-img:${filenameMatch}`;
    // 1) 선택: 이미지 셀 컨테이너의 onClick
    let el = img;
    for (let i = 0; i < 6 && el; i++) {
      const p = propsOf(el);
      if (p && typeof p.onClick === "function") {
        p.onClick({ preventDefault: () => {}, stopPropagation: () => {} });
        break;
      }
      el = el.parentElement;
    }
    // 2) 적용: 같은 셀 안의 "적용하기"
    let cell = img;
    for (let i = 0; i < 6; i++) {
      cell = cell.parentElement;
      if (!cell) break;
      const btn = [...cell.querySelectorAll("button,div")].find(
        (e) => e.textContent.trim() === "적용하기"
      );
      if (btn) {
        const p = propsOf(btn);
        if (p && typeof p.onClick === "function")
          p.onClick({ preventDefault: () => {}, stopPropagation: () => {} });
        else btn.click();
        return `applied:${filenameMatch}`;
      }
    }
    return "selected-but-no-적용하기";
  };

  // ── 카드 순서 변경 (dnd-kit onDragEnd 직접 호출) ───────────────────────
  // 마우스/키보드 이벤트는 dnd-kit이 무시 → DndContext의 onDragEnd 콜백을 fiber에서
  // 찾아 {active, over}로 직접 호출하면 arrayMove reorder가 즉시 동작.
  const _sortableCtx = () => {
    const s = document.querySelector("[aria-roledescription=sortable]");
    if (!s) return null;
    const fk = Object.keys(s).find((k) => k.startsWith("__reactFiber"));
    let fiber = s[fk],
      items = null,
      onDragEnd = null;
    for (let i = 0; i < 60 && fiber; i++) {
      const p = fiber.memoizedProps;
      if (p && p.items && !items) items = p.items;
      if (p && typeof p.onDragEnd === "function" && !onDragEnd) onDragEnd = p.onDragEnd;
      fiber = fiber.return;
    }
    return items && onDragEnd ? { items, onDragEnd } : null;
  };

  // 현재 카드 순서 [{id,type}] (sortable items 기준 = 보드 표시 순서)
  const cardOrder = () => {
    const ctx = _sortableCtx();
    if (!ctx) return [];
    const idType = {};
    for (const el of document.querySelectorAll("div")) {
      let n = fiberOf(el),
        d = 0;
      while (n && d < 2) {
        const b = n.memoizedProps && n.memoizedProps.block;
        if (b && b.id) idType[b.id] = b.type;
        n = n.return;
        d++;
      }
    }
    return ctx.items.map((it) => {
      const id = typeof it === "object" ? it.id : it;
      return { id, type: idType[id] || "?" };
    });
  };

  // 카드 이동: fromIdx(현재 위치) → toIdx(도착 위치). cardOrder() 인덱스 기준.
  const reorderCard = (fromIdx, toIdx) => {
    const ctx = _sortableCtx();
    if (!ctx) return "no-sortable-ctx";
    const items = ctx.items;
    if (fromIdx < 0 || fromIdx >= items.length || toIdx < 0 || toIdx >= items.length)
      return `out-of-range(len=${items.length})`;
    const aid = typeof items[fromIdx] === "object" ? items[fromIdx].id : items[fromIdx];
    const oid = typeof items[toIdx] === "object" ? items[toIdx].id : items[toIdx];
    ctx.onDragEnd({
      active: { id: aid, data: { current: undefined } },
      over: { id: oid, data: { current: undefined } },
      delta: { x: 0, y: 0 },
      collisions: null,
      activatorEvent: null,
    });
    return `moved ${fromIdx}->${toIdx}`;
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
  // ⚠️ 슬롯당 핸들러 2개(행+미리보기)·이중 setter(배경=m / 텍스트·버튼=l)가 각자
  //    stale state를 rebuild → 여러 색을 무조건 연속 설정하면 마지막이 앞을 덮어씀.
  //    ✅ 멀티컬러는 "재조정 루프": 한 색씩 설정 → themeColors()로 확인 →
  //       **되돌아간(불일치) 슬롯만** 다시 setThemeColor → 일치할 때까지(보통 2패스) 반복.
  //       (이미 맞는 슬롯은 건드리지 말 것 — 건드리면 재충돌). SKILL.md 레시피 참고.
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
  // 색상 = openColorPicker → (sleep) → [재조정 루프: setThemeColor 한 색씩 → themeColors() 확인
  //        → 불일치 슬롯만 재설정, 수렴까지 반복] → saveTheme → (sleep) → confirmThemeWarning

  // ── 전체 스냅샷 (파이프라인 검증용) ───────────────────────────────────
  // blocks()는 id→type Map이라 style/content가 없음. dumpState는 모든(마운트된) 카드의
  // full block 객체를 수집(전 div 스캔 → boardRows 높이필터가 놓치는 tall 카드도 포함)하고,
  // sortable items 순서로 정렬한다. 검증 에이전트(V1~V5)·수정(F1)의 입력 스냅샷.
  // ⚠️ 가상화로 화면 밖 카드는 미마운트일 수 있음(보드 스크롤 금지) → missing[]에 id 표시.
  const safeTheme = () => {
    try {
      const t = themeColors();
      return t && (t.배경 || t.텍스트 || t.버튼) ? t : null; // 테마 패널 닫혀있으면 null
    } catch (e) {
      return null;
    }
  };
  const dumpState = () => {
    const map = new Map();
    for (const el of document.querySelectorAll("div")) {
      let n = fiberOf(el),
        d = 0;
      while (n && d < 2) {
        const b = n.memoizedProps && n.memoizedProps.block;
        if (b && b.id && b.type) map.set(b.id, b);
        n = n.return;
        d++;
      }
    }
    const ctx = _sortableCtx();
    if (ctx && ctx.items && ctx.items.length) {
      const order = ctx.items.map((it) => (typeof it === "object" ? it.id : it));
      const ordered = order.map((id) => map.get(id)).filter(Boolean);
      const missing = order.filter((id) => !map.has(id));
      return { blocks: ordered, total: order.length, captured: ordered.length, missing, theme: safeTheme() };
    }
    const ordered = [...map.values()];
    return { blocks: ordered, total: ordered.length, captured: ordered.length, missing: [], theme: safeTheme() };
  };

  window.__cdbd = {
    fiberOf,
    onClickOf,
    boardRows,
    blockOfRow,
    blocks,
    count,
    dumpState,
    openAddModal,
    pickCardType,
    confirmReservation,
    openKebab,
    menuClick,
    confirmSwal,
    openPin,
    pinTo,
    openImageUpload,
    uploadImage,
    applyImage,
    cardOrder,
    reorderCard,
    openColorPicker,
    setThemeColor,
    themeColors,
    saveTheme,
    confirmThemeWarning,
  };
  return "installed";
})();
