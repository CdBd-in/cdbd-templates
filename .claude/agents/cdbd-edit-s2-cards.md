---
name: cdbd-edit-s2-cards
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
