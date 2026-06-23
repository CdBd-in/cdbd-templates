---
name: cdbd-card-automation
description: Use when adding, deleting, duplicating, or reordering cards OR setting page theme colors in the CdBd editor (cdbd.in/editor/{id}) via automation — for 4단계 템플릿 제작. Drives cards/colors through React fiber handlers (onClick·onChange·onDragEnd), not mouse-coordinate clicks. Covers 카드 추가/삭제/복제/순서변경, 페이지 색상(배경·텍스트·버튼 hex), the text-card focus gotcha, and the 예약 카드 credit dialog.
---

# CdBd 카드 자동화 (JS, 좌표 클릭 없음)

## Overview

CdBd 에디터에서 카드 **추가·삭제·복제·순서변경·페이지 색상**을 마우스 좌표 클릭 없이 자동화한다. 핵심 원리: CdBd 에디터의 카드 목록·테마는 React 상태이고, **모달/메뉴 항목의 fiber 콜백(`onClick`·`onChange`·`onDragEnd`)을 JS로 직접 호출**하면 클릭한 것과 동일하게 동작한다. 좌표 클릭보다 빠르고, 가상화(스크롤)·hover 의존 UI에 영향받지 않는다.

[[1-4-1. 에디터 페이지]]의 파일업로드(`onDrop` 직접 호출) 자동화와 같은 계열.

## When to use

- 4단계(에디터 구현)에서 카드 다수를 빠르게 쌓거나/정리할 때
- 이전 세션 잔존 카드 일괄 삭제
- 같은 카드(텍스트·버튼 등) 반복 복제

**When NOT:** 카드 라벨 inline edit, 카드 디자인 슬라이더 세부값(우측 패널) — 별도 패턴(미통합).

## Quick reference (검증: editor 4903)

| 작업 | 방법 | 확인 다이얼로그 |
|---|---|---|
| 추가 (이미지·버튼·프로필·갤러리·위치·구분선·SNS·메뉴·상품·유튜브·Q&A·2열) | 모달 열기 → 타입 항목 onClick | 없음 (모달 자동 닫힘=성공) |
| 추가 (**텍스트**) | 기존 텍스트 카드 **복제** (단일 '텍스트' 모달추가는 불안정) | 없음 |
| 추가 (**예약**) | 타입 항목 onClick → **크레딧 확인 다이얼로그** 1회 더 | "예약 카드 추가하기" (⚠️ 확정은 크레딧 필요) |
| **삭제** | kebab 열기 → '카드 삭제하기' → **SweetAlert 확인** | "삭제하시겠어요?" |
| **복제** | kebab 열기 → '카드 복제하기' | 없음 (예약만 DB조회로 느림) |
| **순서 변경** | dnd-kit `onDragEnd` 직접 호출 (`reorderCard(from,to)`) | 없음 |
| **페이지 색상** (배경·텍스트·버튼) | 색상 더보기 → 슬롯 `onChange("#hex")` 직접 호출 (swatch 클릭 ❌) | 저장 시 "페이지 테마 변경하기" |

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
$B js "window.__cdbd.pickCardType('예약')";   sleep 1.2   # 크레딧 확인 다이얼로그 뜸(검증됨)
$B js "window.__cdbd.confirmReservation()";  sleep 1.2   # "카드 추가하기"(MuiLoadingButton)
```
⚠️ 확인 버튼은 **DB 예약레코드 생성 네트워크 요청**을 띄우는 LoadingButton이라, **크레딧 잔액이 충분해야** 최종 추가가 완료된다. 0-크레딧 계정에선 버튼이 로딩 상태로 멈춤(다이얼로그까지는 정상 동작 검증). 취소는 `취소하기` 버튼 클릭.

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

**카드 순서 변경** (dnd-kit `onDragEnd` 직접 호출 — 마우스/키보드 드래그 시뮬레이션은 모두 실패):
```bash
$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"   # 현재 순서 확인 (인덱스 파악)
$B js "window.__cdbd.reorderCard(8,0)"; sleep 1.2                  # 8번 카드를 0번 위치로 이동
$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"   # 변경 확인
```
- `cardOrder()` = 보드 표시 순서 `[{id,type}]` (dnd-kit `items` prop 기준). `reorderCard(from,to)` = from 인덱스 카드를 to 위치로.
- 연속 이동 시 **매번 cardOrder()로 인덱스 재확인** (한 번 옮기면 인덱스 전부 밀림).
- 드라이버는 **첫 sortable(카드 보드)** 의 onDragEnd를 잡는다. 갤러리·메뉴 내부에도 sortable이 있으나 카드 보드가 첫 번째라 정상 동작. 풀 원리: [[1-4-1. 에디터 페이지#🥇 dnd-kit 드래그앤드롭 자동화 (2026-06-19 기록) — 카드 순서 변경]]

## 페이지 색상 (배경·텍스트·버튼 hex) — swatch 클릭 없이

각 색 슬롯의 React `onChange("#hex")`를 fiber로 직접 호출한다. **swatch(색 원) 클릭·SketchPicker·hex input 필드 전부 불필요, 실제 클릭 0번.** (editor 4903 검증)

슬롯 식별은 **onChange 소스 시그니처**로 한다(위치 인덱스 ❌ — 배경 행 이미지 아이콘 때문에 어긋남): 배경=`base.background` · 텍스트=`base.color` · 버튼=`theme.button.background`. 드라이버 `setThemeColor`가 이 매칭을 처리.

```bash
# 1) 페이지 테마 패널 열기 (헤더 팔레트 아이콘) → 색상 더보기
$B js "[...document.querySelectorAll('button')].filter(b=>{const r=b.getBoundingClientRect();return r.y<90&&r.x>1000&&r.x<1030})[0]?.click()"; sleep 1
$B js "window.__cdbd.openColorPicker()"; sleep 1.2

# 2) 한 색씩 설정
$B js "window.__cdbd.setThemeColor('텍스트','#F5F1E6')"; sleep 1.2
$B js "window.__cdbd.setThemeColor('버튼','#C9A227')";   sleep 1.2
$B js "window.__cdbd.setThemeColor('배경','#0B3D2E')";   sleep 1.2

# 3) 🔁 재조정 루프 (필수) — 되돌아간 슬롯만 다시 설정, 수렴까지 (보통 2패스)
for pass in 1 2 3 4; do
  $B js "window.__cdbd.themeColors().배경!=='#0B3D2E'?window.__cdbd.setThemeColor('배경','#0B3D2E'):'ok'"; sleep 1
  $B js "window.__cdbd.themeColors().텍스트!=='#F5F1E6'?window.__cdbd.setThemeColor('텍스트','#F5F1E6'):'ok'"; sleep 1
  $B js "window.__cdbd.themeColors().버튼!=='#C9A227'?window.__cdbd.setThemeColor('버튼','#C9A227'):'ok'"; sleep 1
done
$B js "JSON.stringify(window.__cdbd.themeColors())"   # 3색 모두 일치 확인

# 4) 저장
$B js "window.__cdbd.saveTheme()";          sleep 1.5   # 변경사항 저장하기
$B js "window.__cdbd.confirmThemeWarning()"; sleep 1.2   # "페이지 테마 변경하기" 경고 → 변경하기
```

**⚠️ 왜 재조정 루프인가:** 슬롯당 핸들러가 2개(행+미리보기)이고, 배경은 setter `m`·텍스트/버튼은 setter `l`로 **서로 다른 theme 복사본**을 각자 stale 상태에서 rebuild한다. 그래서 여러 색을 무조건 연속 설정하면 마지막 호출이 앞 색을 덮어쓴다. **이미 맞는 슬롯은 건드리지 말고 불일치 슬롯만** 재설정하면 2패스 내 수렴(건드리면 재충돌). 단일 색 1개만 바꿀 땐 `setThemeColor` 1회로 충분(루프 불필요).

> 구방식(fallback): onChange가 안 통하는 픽커는 [[CLAUDE.md]] "페이지 색상 — SketchPicker 실제클릭" 항목(색 원 `$B click` + hex `$B fill`). per-card 디자인 보드 색상도 동일 onChange 구조 추정(미검증).

## Common mistakes

| 증상 | 원인·해결 |
|---|---|
| `pickCardType` 했는데 모달 안 닫힘 | 잘못된 래퍼 onClick을 잡음. 드라이버는 **항목 컴포넌트(Icon/title/description prop 보유)** 의 onClick만 매칭해 회피 — 모달이 완전히 렌더된 뒤(>1s) 호출했는지 확인 |
| 단일 '텍스트' 추가가 안 됨 | 정상. 텍스트는 포커스(selected_block_id) 의존 → **복제**로 추가 |
| `count()`가 안 변함 | 가상화로 새 카드가 화면 밖 미마운트. 정상. 스크린샷/모달닫힘으로 판정 |
| `openKebab` "no-kebab-button" | kebab은 hover시 보이지만 DOM엔 존재. 행 매칭 실패가 흔함 → matcher 타입/인덱스 확인. 보드 행 필터는 `x>540 && width>280 && 40<h<90` |
| 예약 카드만 누락 | `confirmReservation()` 안 부름(확인 1회 더). 또는 크레딧 부족으로 LoadingButton 멈춤 — 크레딧 있는 계정에서 실행 |
| 삭제했는데 안 지워짐 | `confirmSwal()` 누락. 삭제는 항상 SweetAlert 확인 필요 |
| 페이지가 대시보드로 튕김 | 모달 X버튼 셀렉터 오타로 다른 요소 클릭됨. 모달 닫기는 추가 성공 시 자동(`i(!1)`). 강제로 닫지 말 것 |

## 내부 동작 (참고)

- 추가: 타입 항목 onClick = `()=>{ t({id:uuid(), type:"image", style:{...theme}, ...}), i(!1) }` — `t`=블록 append setter, `i(!1)`=모달 닫기. setter `t`는 클로저라 단독 추출 불가 → 항목 onClick 호출이 유일 경로.
- 삭제: `async()=>{ if(!(await confirm(...)).isConfirmed)return; ...blocks.filter(b=>b.id!==m.id)... }`
- 복제: `async()=>{ let id=uuid(), clone=rK.X2(m); append({...clone,id}); }` — 예약은 Supabase 조회 추가.
- 식별은 **라벨 아님, fiber `block.type`** ([[CLAUDE.md]] SVG 시그니처 원칙과 동일 취지: DOM 텍스트로 추정 금지).

전체 드라이버: `card-driver.js` (window.__cdbd 메서드: openAddModal, pickCardType, confirmReservation, openKebab, menuClick, confirmSwal, count, blocks, blockOfRow).
