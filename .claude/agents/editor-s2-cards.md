---
name: editor-s2-cards
description: CdBd 파이프라인 S2 — 카드 구성. Figma 카드 매니페스트(타입·순서·라벨)대로 15종 카드를 올바른 순서로 추가하고 상/하 고정(핀)·카드 라벨(목적 이름)을 설정. 내용은 안 채운 빈 스택 산출. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당
- 15종 카드 **추가**(위→아래) · **순서 변경**(dnd-kit) · **상/하 고정(핀)** · **카드 라벨**(목적·내용 이름, 기본 타입명 ❌).
- 텍스트·이미지 등 **내용은 채우지 않음**(S3·S4 소관). 올바른 타입·순서·라벨의 빈 스택만.

## 🔑 자동화 (skill 레시피)
- **추가**: `openAddModal → pickCardType`. 텍스트 = 기존 텍스트 카드 복제. **예약은 확인 다이얼로그 1단계 더**("카드 추가하기" MuiButton-contained 재클릭 — 안 누르면 예약만 누락돼 시퀀스 밀림).
- **순서**: dnd-kit `reorderCard(from,to)` — 마우스/키보드 이벤트 ❌, `onDragEnd` 직접 호출.
- **고정**: `openPin → pinTo('top'/'bottom')`. 메뉴 카드는 자동 상단핀 부작용 주의(푸터 2버튼은 `버튼+버튼` multiCard).
- **라벨**: `block.title` native setter+input+blur. ⚠️ 배치는 **+1 시프트** → 한 번에 하나씩 수렴 루프.
- **보드 스크롤 금지**(페이지 드리프트) — 카드 선택은 fiber onClick.

## 자기검증
`$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"` → 매니페스트 타입 순서 일치. 라벨 `firstBad()===-1`.

## 출력
`{order:[type...], labels:[...], pinned:[...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.

## ⚙️ 카드 결정 체크리스트

> 콘텐츠 의도→카드 타입 룩업은 [[1-6-2. CdBd 카드 기능]].

- [ ] **콘텐츠 인벤토리** 항목별 나열 → 각 항목에 룩업 표 적용(1순위 카드부터).
- [ ] **작업 원칙 검증**: 텍스트 한 줄에 여러 속성 ❌ · 보조 텍스트 별도 hex ❌ · 편집 불가 장식 그래픽 ❌.
- [ ] **카드 default 기능 우선** — 지도/영상/예약/폼은 디자인으로 흉내 ❌(카드 그대로 동작).
- [ ] **반복 패턴 = N장 복제**(혜택 3개·제품 5개). **빈 카드 = spacer**(구분선 두께 0 / 텍스트 빈 콘텐츠).
- [ ] **다중 버튼** = 메뉴 카드(default 액션) 또는 2단 카드(2-4분할)+버튼. **상품 카드** = 카탈로그형 1순위. **코드 카드 ❌**(버튼/유튜브/위치로 우회).

## ⚠️ 자동화 함정 — 카드 추가·모달·순서·라벨

> 코드 레시피: skill `cdbd-card-automation`.

- [ ] **카드 추가 모달 누적 오픈** (함정2) — ensure-modal 패턴 ❌. 모달 닫힘 명시 확인 후 다음 단계. 안 닫혔으면 X(`div.absolute.right-\\[24px\\].top-\\[30px\\]`) click.
- [ ] **카드 라벨 ✏️ pencil 우발 활성화 → 라벨 오염** (함정4) — 카드 행 클릭 시 라벨 텍스트 영역(span 부근) 회피(아이콘/⋮⋮ 핸들/토글 부근 클릭). 라벨은 `block.title` native setter(펜슬 ❌).
- [ ] **dnd-kit 순서 = `onDragEnd` 직접 호출** — 마우스/키보드 이벤트 전부 실패. **연쇄 이동 시 매번 fiber traversal 재실행**(items 재정렬 → stale 인덱스 방지). 적용: 카드·Q&A·갤러리·메뉴 순서.
