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

## 자기검증
`$B js "JSON.parse(window.__cdbd.dumpState().blocks.find(...).content)"` → 텍스트·linebreak 노드 위치가 Figma 줄 구조와 일치.

## 출력
`{filled:[{cardId,text}...], lineBreaksOk:bool}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
