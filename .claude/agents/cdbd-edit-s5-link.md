---
name: cdbd-edit-s5-link
description: CdBd 파이프라인 S5 — 링크·기능. 버튼 링크 6종·위치 지오코딩·Q&A 폼·유튜브·SNS 채널을 설정해 실제 동작하게 만듦. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당
- **버튼/2단 링크 6종**: 전화·문자·이메일·URL·카카오·연락처(vCard).
- **위치 지오코딩**: 주소 → 좌표.
- **Q&A 폼**: 질문 유형·옵션(범용 폼 — RSVP·약관동의·만족도 포함).
- **유튜브·SNS 채널**(SNS 카드는 푸터 아이콘 묶음 전용).

## 🔑 자동화 (skill 레시피)
- 링크 = multiCard/button `onUpdateItem`. **전화 = `type:'call'`(전화하기)**, URL/문자/이메일/카카오/연락처 각 타입.
- **위치 "지도 보기" 버튼은 주소를 검색 드롭다운에서 선택(지오코딩)해야 `lat`/`lng`/`naverMapsUrl` 생성** — 직접 타이핑만 하면 좌표 없어 버튼 안 열림("지도 안 열림"의 흔한 원인). skill `cdbd-card-automation#위치-카드-주소`.
- Q&A 복수선택 토글은 사용자정의 div(24×15, MUI Switch 아님) — 좌표 클릭. 질문 유형 in-place 변경 불가 → 삭제 후 신규 + reorder(onDragEnd).

## 자기검증
`dumpState()`에서 `linkButton.type`·`href` 존재, 위치 `location.lat/lng/naverMapsUrl` 존재.

## 출력
`{links:[...], geocoded:bool, forms:[...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
