---
name: cdbd-edit-s3-text
description: CdBd 파이프라인 S3 — 텍스트 내용. 모든 카드의 텍스트 필드·버튼 텍스트를 정확한 문자열로 채우고 줄바꿈(개행) 위치를 Figma와 일치시킴. 줄간격(디자인)은 V1, 폰트·크기·색·정렬도 V1 소관. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당
- 모든 텍스트 렌더 카드의 **문자열 내용** + **버튼/예약 버튼 텍스트** + **줄바꿈 위치**.
- **줄바꿈 = 내용(S3)** / **줄간격 lineHeight = 디자인(V1)** — 명확히 구분.
- 폰트·크기·색·정렬은 **V1 소관**, S3는 **내용/개행만**.

## 🔑 자동화 (skill 레시피)
- 텍스트 입력 = 카드 보드에서 카드 **명시 클릭**(fiber onClick) → 우측 패널 Lexical contenteditable 입력. 모바일 프리뷰 last-focus 함정(최하단 버튼 텍스트 덮어쓰기) 회피.
- 개행 = Lexical linebreak 노드. multiCard/profile 하위 텍스트도 요소별로.
- 카드 라벨 ✏️ pencil 우발 활성화 회피(라벨 오염).
- **🔑 예약·버튼 카드 텍스트 = 프리뷰 contenteditable 실제 키보드 (2026-07-06 검증)**: 예약 버튼/버튼 카드 텍스트는 `block.content` mutate가 **리버트**(카드 자체 저장 체계). → **미리보기 보드에서 해당 요소 직접 클릭 focus → `$B press Meta+a`(전체선택) → `$B type "..."`**. `execCommand('insertText')`는 Lexical에서 무반응 ❌. 정확한 요소 타게팅으로 최하단 버튼 focus 함정 회피.

## 자기검증
`$B js "JSON.parse(window.__cdbd.dumpState().blocks.find(...).content)"` → 텍스트·linebreak 노드 위치가 Figma 줄 구조와 일치.

## 출력
`{filled:[{cardId,text}...], lineBreaksOk:bool}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.

## ✅ 체크리스트 (2026-07-06 5025 교훈)
- [ ] 다줄 텍스트(헤드라인 등)는 Figma 줄 구조대로 **linebreak 삽입** — 1줄 방치 시 모바일서 단어 중간 깨짐(예: "…40주년 감/사 연합예배").
- [ ] 모든 텍스트 정렬 = Figma(일반 텍스트 left, 예약/버튼 center)를 **content paragraph format**으로 설정.
- [ ] **multiCard 내부 텍스트**(제목열·요약열)도 정렬 확인 — 기본 center로 남기 쉬움, Figma가 left면 left.
- [ ] 예약/버튼 카드 텍스트는 **프리뷰 contenteditable 실제 키보드**로(block.content mutate는 리버트).
- [ ] **복합 정보 텍스트(예: 세션 일시 = 날짜/시간, 주소 = 도로명/상세)** 는 Figma가 여러 줄이면 요소 내 **linebreak로 줄 분리** — 짧아 보여도 한 줄로 뭉치지 말 것(2026-07-07 5025: '세션 일시' 줄바꿈 누락).

## ⚠️ 자동화 함정 — Lexical 텍스트 입력

> 코드 레시피: skill `cdbd-card-automation`.

- [ ] **"last contenteditable" = 최하단 버튼 텍스트** (함정1·13) — 새 텍스트 카드 후 마지막 contenteditable에 focus하면 페이지 최하단 버튼 텍스트가 덮어써짐. **카드 보드에서 새 카드 명시 클릭 → 우측 패널 입력**(mobile preview 의존 ❌, 마운트 시간차).
- [ ] **Lexical 다줄 = 한 줄씩 type + Enter** (함정16) — paste의 `\n`은 단일 paragraph로 뭉침. `$B type "줄1"; $B press Enter; $B type "줄2"`.
- [ ] **완전 클리어 = Meta+A→Backspace 2회** (함정17) — 1회는 selection만 지움 → 텍스트 잔존/중복. `Meta+A;Backspace;Meta+A;Backspace`.
- [ ] **shell 예약 문자(`|`·`~`·`#`·`$`) `$B type` 실패** (함정18) — `|`=`$B press "Shift+Backslash"`, `~`=`$B press "Shift+Backquote"`. 일반 ASCII만 `$B type`.
