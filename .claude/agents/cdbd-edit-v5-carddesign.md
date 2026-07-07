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

## ✅ 체크리스트 (2026-07-06 5025 교훈)
- [ ] 배경·채움/아웃라인·모서리·내부여백 비교.
- [ ] **방향성 외부여백/패딩(상/하/좌/우 개별) = 가능** — 여백 컨트롤 **우측 아코디언 버튼(chevron)** 클릭 → 상/하/좌/우 개별 필드 노출 → **텍스트 필드 키보드 입력**(영속). block.style.margin/padding mutate는 리버트 → 반드시 아코디언 UI.
- [ ] 값은 CSS shorthand로 저장(예: `margin '0px 20px'`=좌우20 인셋 플로팅 카드 / `padding '4px 20px 8px'`=상4·좌우20·하8 타이트).
- [ ] **상하 여백 내부(padding)+외부(margin) 중복 적용 금지** — 같은 상하 간격이 padding과 margin 양쪽에 들어가 간격이 두 배가 되지 않았는지 확인. 상하 간격은 한쪽(보통 padding)만(2026-07-07 5025: 내부/외부 중복 점검).
- [ ] **최하단(마지막) 카드 하단 여백 ≥ 40** — page gap=0이라 페이지 끝 여백은 마지막 카드 padding-bottom(또는 하단 여백 카드)으로 표현, 콘텐츠가 화면 끝에 붙지 않게(2026-07-07 5025).
- [ ] **각 카드 상하 패딩을 시안 프레임 값과 대조 (값 자체가 과다한지)** — CdBd 기본 20px 균일은 시안보다 넓은 경우 많음(예: 로고↔타이틀 gap CdBd 40 vs 시안 16). page gap=0 → **카드A 하단 padding + 카드B 상단 padding = 실제 카드 간격**. 시안 각 프레임 내부 top/bottom offset(get_design_context `pt-`/`pb-`)을 카드 padding 상/하로 매칭. '중복 없음'만 보지 말 것(2026-07-07 5025: 14카드 20/20 → per-card 시안값으로 좁힘).
- [ ] **좌우(L/R) 패딩도 카드별 실측 — 20 상수 가정 금지** — 상하만 보지 말 것. 시안 각 프레임의 `pl-`/`pr-`(또는 좌우 offset)을 실측해 좌우 padding으로 매칭(예: 시안 28px인데 CdBd 기본 20이면 diff). '상하 여백' 지적에 갇혀 좌우를 default 20으로 두면 유실(2026-07-07 5025: 좌우 28→전부 20 미스).
- [ ] **multiCard(2단)·reservation은 내부 여백 레이어를 별도 비교** — `block.style.padding`(카드 외곽) 외에 2단 카드 **내부 셀/아이템 여백**이 따로 존재. 외곽 padding만 맞추고 내부를 방치하지 말 것(2026-07-07 5025: 전체 회차 2단 카드 내부 상하여백 오적용). multiCard 여백은 MuiCollapse 패널 경로(헤더 먼저 펼침) + blur 커밋 필수(shared 영속화 표) — 배치서 revert 나기 쉬우니 리로드 후 재검증.

## ⚠️ 자동화 함정 — 카드 디자인 패널

> 코드 레시피: skill `cdbd-card-automation`.

- [ ] **MUI Collapse 닫힌 섹션 element = `visibility:hidden`** (함정15) — `getBoundingClientRect()`·`aria-pressed`는 정상이라 클릭 가능해 보이지만 `$B click` timeout. 같은 텍스트 버튼이 여러 개면(예: 위치 카드 "둥근" 2개) **`getComputedStyle(el).visibility==="visible"` 필터 필수**. 작업 섹션만 펼치기.
- [ ] **카드 디자인 accordion 상태는 카드 전환 시 reset** (함정21) — 카드마다 카드 디자인 펼치기 → 여백 accordion expand 반복(helper 함수화).
