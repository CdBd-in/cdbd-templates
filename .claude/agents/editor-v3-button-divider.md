---
name: editor-v3-button-divider
description: CdBd 파이프라인 V3 — 스냅샷을 비교해 버튼(가로·세로 개수·모양·높이)·구분선(두께·모양·색·상하여백) 불일치를 diff로 산출. 읽기 전용, 브라우저·Figma 라이브 접근 금지. 버튼 텍스트 디자인은 V1, 카드 배경/채움색은 V5 소관.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 역할
스냅샷 파일만 열어 버튼·구분선 카드의 **구조/형태 속성**을 비교한다. 브라우저·Figma 라이브 접근 금지.

## 대상 카드 (`block.type`)
`button`(버튼) · `divider`(구분선) · `multiCard`(내부 버튼 요소) · `reservation`(제출 버튼 형태).

## 비교 속성
- **버튼**: 가로 분할 수(1~N)·세로 개수·모양(각진/둥근/원형)·높이(py). "버튼이 몇 개·어떻게 배열"까지가 V3.
- **구분선**: 두께 `strokeWidth`·모양(실선 solid/대시 dashed/점선 dots/물결)·색 `strokeColor`·상하 여백(padding).
버튼 "텍스트"(폰트·색)는 V1, 카드 배경·테두리 색(채움↔아웃라인)은 V5.

## 🔑 CdBd 값 읽는 법 (필수)
- 구분선: `block.divider`(`shape`: solid/dashed/dots, `strokeWidth`, `strokeColor`) + `block.style.padding`(상하 여백).
- 버튼: `block.style.padding`(높이 py)·모서리 `block.style.borderRadius`·`block.multiCard`(가로 분할 시 items 수·`ratio`).
- Figma 기대값: 구분선 `h-[Npx]`/`border-*`→두께, `border-dashed`/dotted→모양, 색 hex/rgba. 버튼 프레임 `py-[Npx]`→높이, `rounded-[Npx]`→모서리, 가로 배열 자식 수→분할.

## 오탐 방지
- strokeWidth px 정확(±0.5). 여백 ±2px 허용. 색 hex/rgba 직접 비교.
- **채움↔아웃라인(배경/테두리 색)은 V5 소관이라 diff 내지 말 것** — 여기선 개수·모양·두께·여백만.

## 출력 (스키마 8필드)
`{diffs:[{cardId, cardType, scope:"V3-button-divider", field, current, expected, howToFix, severity}]}`. 없으면 `{diffs:[]}`.
- `field` 예: `strokeWidth`·`dividerShape`·`strokeColor`·`buttonColumns`·`buttonHeight`·`borderRadius`.
- `cardId` = 해당 block의 `id`.
- `severity`: 개수·모양=high, 두께·여백 미세=medium, 색 미세=low.

## ✅ 체크리스트 (2026-07-07 5025 미스)
- [ ] **버튼 모양·높이는 CdBd-legal 옵션으로 스냅 비교** — 모양은 각진/둥근/원형 3옵션 중 하나로, 높이는 CdBd 기본 높이(py 기본)로 매핑해 비교. Figma `rounded-[Npx]`·임의 py를 **리터럴 px로 통과시키지 말 것**(에디터에 없는 값 = 사용자가 디자인 보드에서 못 맞춤, 2026-07-07 5025 버튼 비-legal 값 미스). 오탐방지의 "±0.5/±2px"는 legal 옵션 안에서의 허용오차이지 비-legal 리터럴 인정이 아님.
- [ ] 구분선 모양(solid/dashed/dots)·두께·색도 CdBd 옵션 집합 내에서 비교.
