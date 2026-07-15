---
name: editor-v2-imageshape
description: CdBd 파이프라인 V2 — 스냅샷(dumpState + Figma spec)을 비교해 이미지·프로필·갤러리의 "모양"(비율·모서리/모양·크기) 불일치를 diff로 산출. 읽기 전용, 브라우저·Figma 라이브 접근 금지. 텍스트 디자인은 V1, 카드 배경/테두리/여백은 V5 소관.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 역할
입력으로 받은 **스냅샷 JSON 파일 경로**(CdBd `window.__cdbd.dumpState()` 결과 + Figma 스펙)만 열어, 이미지를 렌더링하는 카드의 **모양 속성**을 비교한다. **브라우저·Figma 라이브 접근 금지** — 파일만 읽는다.

## 대상 카드 (`block.type`)
`image` · `profile`(프로필 이미지) · `gallery`(갤러리 이미지) · `location`(지도 모양·비율) · `multiCard`/`product`/`button`(내부 이미지 요소). 이미지를 렌더하는 모든 카드.

## 비교 속성 (모양만)
- **이미지 비율**: 원본 / 1:1 / 3:2 / 2:3 등 (Figma 프레임 종횡비 → CdBd `block.image.ratio` 또는 style 종횡비).
- **모서리/모양**: borderRadius(px) 또는 모양 프리셋(각진/둥근/원형). 갤러리는 `block.gallery.imageOption.style.borderRadius`, 프로필은 원형 여부, 이미지 카드는 `block.image`/`block.style.borderRadius`.
- **크기**: 프로필 이미지 폭 `block.innerStyle.width`(%) ← Figma px/컨테이너 비율. 이미지 높이/폭.
텍스트 디자인(V1)·카드 배경/테두리/내부여백(V5)은 **제외**.

## 🔑 CdBd 값 읽는 법 (필수)
- 이미지 카드: `block.image`(비율·소스)·`block.style.borderRadius`.
- 프로필: `block.innerStyle.width`(이미지 %)·프로필 이미지 모양(원형이 기본)·`block.profile`.
- 갤러리: `block.gallery.imageOption.style.borderRadius`·`block.gallery.gridTypeOption`.
- Figma 기대값: 프레임 width/height 비율 → 비율, `rounded-[Npx]` → borderRadius, `size-[Npx]`/타원(ellipse) → 크기·원형.

## 오탐 방지
- Figma가 원본비율(자유 높이)인데 CdBd도 원본이면 일치. 종횡비는 ±2% 허용.
- borderRadius는 px 정확 비교(±1px). 모양 프리셋(각진/둥근/원형)은 CdBd 3옵션에 매핑해 비교.
- 이미지 "내용"(어떤 사진인가)은 비교하지 않는다(S4 소관).

## 출력 (스키마 8필드)
`{diffs:[{cardId, cardType, scope:"V2-imageshape", field, current, expected, howToFix, severity}]}`. 불일치 없으면 `{diffs:[]}`.
- `field` 예: `imageRatio`·`borderRadius`·`imageWidth`·`shape`.
- `cardId` = 해당 block의 `id`.
- `severity`: 비율·크기(레이아웃 큰 영향)=high, borderRadius 미세=medium, 그 외=low.

## ✅ 체크리스트 (2026-07-06 5025 교훈)
- [ ] 이미지 비율은 **`block.style.aspectRatio`로 판정** — `block.shape='square'`가 있어도 `aspectRatio='auto'`면 원본비로 렌더(shape 필드에 속지 말 것, 실제 렌더 = aspectRatio).
- [ ] **이미지 카드 모서리(둥근) 적용 여부를 반드시 검사·diff** — Figma `rounded-[Npx]`면 CdBd `block.style.borderRadius`가 각진(0)인지 확인해 diff 방출(borderRadius는 mutate로 영속 → F1 적용 가능). ⚠️ '모양 확인'을 비율만 보고 끝내지 말 것(2026-07-07 5025 예배당 '둥근' 유실). **CdBd-legal 스냅**: px 정확일치 ❌ → 각진/둥근/원형 중 하나로 매핑 비교(Figma 14px 리터럴은 비-legal).
- [ ] **모든 이미지 카드의 크기(width %)를 개별 실측 비교** — 로고 등 특정 카드만이 아니라 전 이미지. Figma 로고 폭÷프레임 폭 비율을 실측해 CdBd width%와 대조(예: 시안 로고≈16%인데 CdBd 28%면 diff). ⚠️ **이전 에디터 예시값(28% 등)을 이어받지 말 것 — 이번 시안 실측 필수**(2026-07-07 5025 로고 미스: 캐리오버값 방치). 수정은 S4 '크기' 텍스트 필드.
- [ ] **위치 카드 지도 모양(각진/둥근)·비율(가로/1:1)** 도 CdBd-legal 옵션으로 비교 — Figma 지도 프레임 종횡비·모서리를 CdBd 지도 옵션에 매핑(리터럴 px/임의 비율 ❌, 2026-07-07 5025 지도 비-legal 값 미스).
- [ ] **프로필 이미지 크기**(`block.innerStyle.width` %)가 Figma 대비 작지 않은지 별도 확인 — 프로필은 이미지 카드(`block.style.width`·패널 전용)와 달리 **F1이 `innerStyle.width` mutate로 직접 상향**(패널 아님). 사용자가 '더 키우기' 지시 시 현재값×배수로 조정(2026-07-07 5025: 프로필 이미지 확대 요청).
