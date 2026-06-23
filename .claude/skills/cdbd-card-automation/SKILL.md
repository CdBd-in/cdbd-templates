---
name: cdbd-card-automation
description: Use when adding, deleting, or duplicating cards in the CdBd editor (cdbd.in/editor/{id}) via automation — for 4단계 템플릿 제작. Drives cards through React fiber onClick handlers (JS), not mouse-coordinate clicks. Covers 카드 추가/삭제/복제, the text-card focus gotcha, and the 예약 카드 credit dialog.
---

# CdBd 카드 자동화 (JS, 좌표 클릭 없음)

## Overview

CdBd 에디터에서 카드 **추가·삭제·복제**를 마우스 좌표 클릭 없이 자동화한다. 핵심 원리: CdBd 에디터의 카드 목록은 React store 상태이고, **모달/메뉴 항목의 fiber `onClick` 핸들러를 JS로 직접 호출**하면 클릭한 것과 동일하게 카드가 추가/삭제/복제된다. 좌표 클릭보다 빠르고, 가상화(스크롤)·hover 의존 UI에 영향받지 않는다.

[[1-4-1. 에디터 페이지]]의 dnd-kit 순서변경·파일업로드 자동화와 같은 계열(React fiber 콜백 직접 호출). 카드 **순서 변경**은 그 문서의 `onDragEnd` 직접 호출 방식을 쓴다(본 skill 범위 밖).

## When to use

- 4단계(에디터 구현)에서 카드 다수를 빠르게 쌓거나/정리할 때
- 이전 세션 잔존 카드 일괄 삭제
- 같은 카드(텍스트·버튼 등) 반복 복제

**When NOT:** 카드 라벨 inline edit, 카드 디자인 슬라이더 세부값(우측 패널) — 별도 패턴. 순서 변경 — dnd-kit `onDragEnd`.

## Quick reference (검증: editor 4903)

| 작업 | 방법 | 확인 다이얼로그 |
|---|---|---|
| 추가 (이미지·버튼·프로필·갤러리·위치·구분선·SNS·메뉴·상품·유튜브·Q&A·2열) | 모달 열기 → 타입 항목 onClick | 없음 (모달 자동 닫힘=성공) |
| 추가 (**텍스트**) | 기존 텍스트 카드 **복제** (단일 '텍스트' 모달추가는 불안정) | 없음 |
| 추가 (**예약**) | 타입 항목 onClick → **크레딧 확인 버튼** 1회 더 | "예약 카드 추가하기" |
| **삭제** | kebab 열기 → '카드 삭제하기' → **SweetAlert 확인** | "삭제하시겠어요?" |
| **복제** | kebab 열기 → '카드 복제하기' | 없음 (예약만 DB조회로 느림) |

## Setup

드라이버를 페이지에 1회 설치한다(에디터 URL 로드 후):

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"   # gstack browse
DRV=".claude/skills/cdbd-card-automation/card-driver.js"
$B goto https://www.cdbd.in/editor/{id}; sleep 4
$B eval "$DRV"                       # → 'installed'  (window.__cdbd 설치)
$B js "JSON.stringify(window.__cdbd.count())"   # 마운트된 카드 수/타입 (대략치)
```

`count()`는 **화면에 마운트된 카드만** 센다(보드 가상화). 절대수 신뢰 불가 → 성공 판정은 **모달이 닫혔는지 / 스크린샷**으로 한다.

## Recipes

단계 사이에 모달·메뉴·다이얼로그 렌더 대기(`sleep ~1.2`)가 **필수**. async eval 금지, bash `sleep`으로 끊는다.

**카드 추가 (텍스트 제외 모든 타입):**
```bash
$B js "window.__cdbd.openAddModal()";        sleep 1.2
$B js "window.__cdbd.pickCardType('이미지')"; sleep 1.2
# 성공 = 모달이 닫힘:
$B js "[...document.querySelectorAll('div')].some(e=>e.textContent.trim()==='카드 추가하기'&&e.getBoundingClientRect().width>300)?'OPEN(실패)':'CLOSED(추가됨)'"
```

**텍스트 카드 추가 = 기존 텍스트 카드 복제** (단일 '텍스트' 모달추가는 포커스 의존이라 JS로 안 생김):
```bash
$B js "window.__cdbd.openKebab({type:'text'})"; sleep 1
$B js "window.__cdbd.menuClick('카드 복제하기')"; sleep 1.2
```

**예약 카드 추가** (크레딧 확인 1회 더):
```bash
$B js "window.__cdbd.openAddModal()";        sleep 1.2
$B js "window.__cdbd.pickCardType('예약')";   sleep 1.2
$B js "window.__cdbd.confirmReservation()";  sleep 1.2   # "카드 추가하기"(contained) 버튼
```

**카드 삭제** (matcher: `{type:'image'}` | `{id:'...'}` | `{index:N}`):
```bash
$B js "window.__cdbd.openKebab({type:'image'})";   sleep 1
$B js "window.__cdbd.menuClick('카드 삭제하기')";   sleep 1.2
$B js "window.__cdbd.confirmSwal()";               sleep 1.2   # SweetAlert 확인
```

**카드 복제:**
```bash
$B js "window.__cdbd.openKebab({type:'button'})";  sleep 1
$B js "window.__cdbd.menuClick('카드 복제하기')";   sleep 1.2
```

**일괄 작업:** 삭제/복제 후 행이 다시 정렬되므로 **매번 openKebab을 다시** 호출한다(이전 행 참조 무효). 추가도 매번 openAddModal부터.

## Common mistakes

| 증상 | 원인·해결 |
|---|---|
| `pickCardType` 했는데 모달 안 닫힘 | 잘못된 래퍼 onClick을 잡음. 드라이버는 `ADD_SIG` 정규식으로 추가 핸들러만 매칭 — 모달이 완전히 렌더된 뒤(>1s) 호출했는지 확인 |
| 단일 '텍스트' 추가가 안 됨 | 정상. 텍스트는 포커스(selected_block_id) 의존 → **복제**로 추가 |
| `count()`가 안 변함 | 가상화로 새 카드가 화면 밖 미마운트. 정상. 스크린샷/모달닫힘으로 판정 |
| `openKebab` "no-kebab-button" | kebab은 hover시 보이지만 DOM엔 존재. 행 매칭 실패가 흔함 → matcher 타입/인덱스 확인. 보드 행 필터는 `x>540 && width>280 && 40<h<90` |
| 예약 카드만 누락 | `confirmReservation()` 안 부름. 다른 카드와 달리 확인 버튼 1회 더 |
| 삭제했는데 안 지워짐 | `confirmSwal()` 누락. 삭제는 항상 SweetAlert 확인 필요 |
| 페이지가 대시보드로 튕김 | 모달 X버튼 셀렉터 오타로 다른 요소 클릭됨. 모달 닫기는 추가 성공 시 자동(`i(!1)`). 강제로 닫지 말 것 |

## 내부 동작 (참고)

- 추가: 타입 항목 onClick = `()=>{ t({id:uuid(), type:"image", style:{...theme}, ...}), i(!1) }` — `t`=블록 append setter, `i(!1)`=모달 닫기. setter `t`는 클로저라 단독 추출 불가 → 항목 onClick 호출이 유일 경로.
- 삭제: `async()=>{ if(!(await confirm(...)).isConfirmed)return; ...blocks.filter(b=>b.id!==m.id)... }`
- 복제: `async()=>{ let id=uuid(), clone=rK.X2(m); append({...clone,id}); }` — 예약은 Supabase 조회 추가.
- 식별은 **라벨 아님, fiber `block.type`** ([[CLAUDE.md]] SVG 시그니처 원칙과 동일 취지: DOM 텍스트로 추정 금지).

전체 드라이버: `card-driver.js` (window.__cdbd 메서드: openAddModal, pickCardType, confirmReservation, openKebab, menuClick, confirmSwal, count, blocks, blockOfRow).
