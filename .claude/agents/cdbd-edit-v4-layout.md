---
name: cdbd-edit-v4-layout
description: CdBd 파이프라인 V4 — 스냅샷을 비교해 레이아웃 유형(프로필 기본/강조/명함형·갤러리 나열/넘겨보기/그리드+단수·메뉴·2단 분할·Q&A 정렬 등) 불일치를 diff로 산출. 읽기 전용, 브라우저·Figma 라이브 접근 금지.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 역할
스냅샷 파일만 열어 각 카드의 **레이아웃 유형/배치**를 비교한다. 브라우저·Figma 라이브 접근 금지.

## 대상 카드 (`block.type`)
`profile` · `gallery` · `menu` · `multiCard`(2단) · `product` · Q&A. 유형 선택이 있는 모든 카드.

## 비교 속성 (유형/배치만)
- **프로필**: 기본형(이미지 위+텍스트 아래 중앙) / 강조형 / 명함형(이미지 좌+텍스트 우 가로). Figma 배치(세로 stack vs 가로 row)로 판정.
- **갤러리**: 나열 / 넘겨보기(자동넘김·인디케이터·화살표) / 그리드(+`gridTypeOption.column` 단수·`rowGap`/`columnGap`).
- **메뉴**: 한눈에 / 햄버거(+프리셋).
- **2단(multiCard)**: 2~4분할·`ratio`(비율)·`align`.
- **상품**: 그리드 / 바.
- **Q&A**: 제목 정렬(중앙 필수)·질문 간격.

## 🔑 CdBd 값 읽는 법 (필수)
- 프로필: `block.profile` 레이아웃 유형 + 이미지/텍스트 방향(가로=명함형).
- 갤러리: `block.gallery.type`(나열/넘겨보기/그리드)·`gridTypeOption.column`·자동넘김 플래그·인디케이터/화살표.
- multiCard: `block.multiCard.items.length`(분할 수)·`ratio`·`align`.
- Figma 기대값: 프레임 방향(flex-col=세로, flex-row=가로)·자식 수(분할)·그리드 열 수.

## 오탐 방지
- 유형 매핑은 CdBd 옵션 집합에 한정(임의 유형 만들지 말 것).
- 텍스트 디자인(V1)·이미지 모양(V2)·카드 배경(V5)은 제외.

## 출력 (스키마 8필드)
`{diffs:[{cardId, cardType, scope:"V4-layout", field, current, expected, howToFix, severity}]}`. 없으면 `{diffs:[]}`.
- `field` 예: `profileLayout`·`galleryType`·`gridColumn`·`splitCount`·`ratio`·`qnaAlign`.
- `cardId` = 해당 block의 `id`.
- `severity`: 유형 자체(프로필형·갤러리형·분할수)=high, 간격·비율 미세=medium.
