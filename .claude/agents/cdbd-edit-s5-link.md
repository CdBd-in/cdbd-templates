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
- **🔑 위치 카드 옵션 = 패널 토글 fiber onClick (2026-07-06 검증)**: `block.location.label/button/address` mutate는 **리버트**. 패널의 **'주소 표시'(label)·'지도 보기 버튼'(button) 칩 onClick**을 `label:!prev`로 직접 호출(연속 조작 시 fiber 재쿼리로 stale-closure 회피). 좌표(lat/lng)는 유지 → 지도 렌더 남음. **Google 타입 위치카드는 지오코더가 영문 주소 반환·한글 타이핑 미커밋(structural)** → 한글 주소는 위 별도 텍스트 카드로 표시(지도 좌표는 정상). 한글 라벨 필요 시 네이버맵 타입 전환+재지오코딩.

## 자기검증
`dumpState()`에서 `linkButton.type`·`href` 존재, 위치 `location.lat/lng/naverMapsUrl` 존재.

## 출력
`{links:[...], geocoded:bool, forms:[...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.

## ✅ 체크리스트 (2026-07-06 5025 교훈)
- [ ] 위치 주소 = 검색 드롭다운 선택(지오코딩)으로 lat/lng 생성 — 직접 타이핑만 ❌("지도 안 열림" 원인).
- [ ] 위치 옵션(주소 표시 label·지도 보기 버튼) 필요에 맞게 **패널 토글** on/off — block.location mutate는 리버트. 연속 토글은 fiber 재쿼리.
- [ ] Google 위치카드 한글 주소는 지오코더 영문 반환(structural) → 한글은 **별도 텍스트카드**로 표시(좌표·지도는 정상).
- [ ] 버튼 링크 6종 onUpdateItem(전화=`type:'call'`).

## ⚠️ 자동화 함정 — Q&A 폼

> 코드 레시피: skill `cdbd-card-automation`.

- [ ] **Q&A 질문 유형 in-place 변경 불가** (함정11) — kebab은 복제/삭제만. **삭제 → 객관식 신규 추가**(마지막 배치) → `onDragEnd`로 reorder.
- [ ] **객관식 input 구조** (함정12) — 인풋0=질문, 인풋1~=옵션, "옵션 추가" 버튼 N번. **복수선택 토글 = 24×15 사용자정의 div**(MUI Switch 아님, 활성 시 `bg: var(--color-information)` + inner `translateX(9px)`) → 좌표 직접 click.
