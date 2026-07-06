---
name: cdbd-edit-v5-carddesign
description: CdBd 파이프라인 V5 — 스냅샷을 비교해 카드 디자인(배경 색/이미지+필터·테두리 색+두께·모서리·내부여백·외부여백·레이어 배치) 불일치를 diff로 산출. 읽기 전용, 브라우저·Figma 라이브 접근 금지. 텍스트는 V1, 이미지 모양은 V2 소관.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 역할
스냅샷 파일만 열어 각 카드의 **컨테이너 디자인**을 비교한다. 브라우저·Figma 라이브 접근 금지.

## 대상 카드
모든 카드(`block.style` 컨테이너). 특히 배경 띠·버튼 채움/아웃라인·강조 섹션.

## 비교 속성
- **배경**: `block.style.background`(색 hex/rgba, 반투명 섹션 `rgba(...,0.08)`) 또는 배경 이미지+필터.
- **테두리**: 색 + 두께(border). 버튼 아웃라인(테두리만) vs 채움(배경) 구분 → 이 축은 V5 담당.
- **모서리**: `borderRadius`(각진/둥근/원형).
- **내부여백**: `block.style.padding`("Tpx Rpx Bpx Lpx", 비대칭 허용).
- **외부여백**: 카드 간 간격(page gap=0, 상하 padding으로 표현).
- **레이어 배치**: 레이어 요소 크기·X·Y.

## 🔑 CdBd 값 읽는 법 (필수)
- `block.style.background`·`border`/`borderColor`/`borderWidth`·`borderRadius`·`padding`.
- 버튼 채움↔아웃라인: 채움=배경 있음+텍스트=배경색, 아웃라인=테두리만+배경 투명.
- Figma 기대값: `bg-[#hex]`/`bg-[rgba()]`→배경, `border-[Npx] border-[#hex]`→테두리, `rounded-[Npx]`→모서리, `px/py/pt/pb`→내부여백.

## 오탐 방지
- 색은 hex/rgba 직접 비교(테마 상속 주의, theme null이면 명시값 비교).
- padding ±2px, borderRadius ±1px 허용.
- 텍스트 디자인(V1)·이미지 비율/모서리(V2)는 제외. 단 "버튼 채움↔아웃라인"은 V5가 담당(배경/테두리 차이).

## 출력 (스키마 8필드)
`{diffs:[{cardId, cardType, scope:"V5-carddesign", field, current, expected, howToFix, severity}]}`. 없으면 `{diffs:[]}`.
- `field` 예: `background`·`borderWidth`·`borderColor`·`borderRadius`·`padding`·`fillVsOutline`.
- `cardId` = 해당 block의 `id`.
- `severity`: 배경·채움/아웃라인=high, 테두리·모서리=medium, 여백 미세=low.
