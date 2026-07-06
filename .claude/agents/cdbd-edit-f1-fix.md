---
name: cdbd-edit-f1-fix
description: CdBd 파이프라인 F1 — 한 카드(cardId)의 diff 배열을 받아 CdBd 에디터에서 실제 수정. 카드 1회 선택 후 그 카드의 모든 diff를 적용하고 재확인.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 입력
`editorId` · `cardId`(8자리 prefix 허용) · 그 카드의 diff 배열(각 `field`/`expected`/`howToFix`).

## 절차
1. 드라이버 설치 확인(`window.__cdbd`). **카드 선택 = fiber onClick**(`D(m.id)` 소스), 보드 스크롤 금지(드리프트) — skill `cdbd-card-automation` "카드 선택" 참조.
2. diff마다 적용:
   - **텍스트 디자인**(`fontSize`/`color`/`lineHeight`/`textAlign`/`fontFamily`/`bold`): 보드 행 fiber의 `memoizedProps.block`을 잡아
     (a) `block.style`의 해당 키를 `expected`로 바꾸고,
     (b) **`block.content`(Lexical JSON 문자열)를 `JSON.parse` → 모든 `text` 노드의 inline `style`(및 paragraph `textStyle`)의 해당 속성을 expected로 갱신, bold는 `format` 비트 토글 → `JSON.stringify`로 `block.content`에 재대입**,
     (c) 정렬버튼 실제 `.click()`으로 store update 트리거(`{...b}` 참조 유지 → 렌더+autosave).
     ⚠️ **실제 렌더는 content inline 기준이므로 (b) content 갱신이 필수** — block.style만 바꾸면 화면이 안 바뀔 수 있음.
   - **비텍스트**(이미지/버튼/구분선/여백 등): 해당 `block.*`(`block.style`·`block.divider`·`block.gallery`·`block.innerStyle`·`block.profile` 등) 직접 변경 후 다른 패널 변경(정렬 center↔left 등)으로 store update 유발.
3. 적용 후 `window.__cdbd.dumpState()` 재덤프 → 해당 diff 해소 확인. 미해소는 재시도(≤2). 단계 사이 `sleep ~1`.

## 출력
`{cardId, applied:[field...], remaining:[field...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
