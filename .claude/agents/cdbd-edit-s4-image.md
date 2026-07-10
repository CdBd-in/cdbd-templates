---
name: cdbd-edit-s4-image
description: CdBd 파이프라인 S4 — 이미지. 준비된 이미지 파일을 슬롯↔이미지 매핑대로 업로드·적용하고 순서를 맞춤(카드/레이어 배경 이미지 포함). 사이즈·모양·비율은 V2 소관. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당
- 모든 이미지 슬롯(이미지 카드·로고·프로필·갤러리·2단 내부·상품·카드/레이어 배경) **업로드·적용·순서**.
- 이미지 **모양/비율/크기는 V2**, **어떤 이미지인가(내용)만 S4**.

## 🔑 자동화 (skill 레시피)
- transient `<input type=file>` 후킹 ❌ → **React `onDrop` 핸들러 직접 호출**(함정23). `openImageUpload → uploadImage(onDrop, dataTransfer) → applyImage`. 소스 JPEG 리사이즈 base64 주입. Bash base64 → `$B js` inject → File → dropzone.onDrop 직접 호출.
- 갤러리 다중 이미지 순서는 dnd-kit `onDragEnd`.
- 이미지 **파일 생성은 S4 밖**([[1-5. 이미지]] — OpenAI gpt-image-1/Thiings/Unsplash). S4는 준비된 파일을 적용만.
- **🔑 이미지 크기(로고 소형화 등) = 이미지 패널 '크기' (2026-07-06 검증)**: `block.style.width` mutate는 **리버트**. **🥇 슬라이더 우측 텍스트 필드(number input)에 실제 키보드 입력**(`$B click 필드 → Meta+a → $B type "N" → Enter`) — 슬라이더보다 정확·안정(우측 필드 있으면 항상 이 방식). 필드 없으면 폴백으로 슬라이더 fiber onChange `onChange({target:{value:N,valueAsNumber:N}}, N)`. 커밋 결과 `style.width='N%'` 리로드 유지(예: 로고 100→28%). 같은 패널 **비율**(원본/1:1/가로/세로)·**정렬** 칩은 fiber onClick. block.style로 되는 것: `aspectRatio`·`borderRadius`. 안 되는 것: `width`(크기).

## 자기검증
스크린샷으로 렌더 확인 + `dumpState()`에서 image 참조 존재.

## 출력
`{applied:[{cardId,slot}...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.

## ✅ 체크리스트 (2026-07-06 5025 교훈)
- [ ] 모든 이미지 슬롯 업로드·적용(로고·프로필·메인·갤러리).
- [ ] **프로필 이미지**: 아바타 placeholder 클릭 → onDrop 업로드 — 빈 상태 방치 ❌(생성물 준비: gpt-image-1 등).
- [ ] **이미지 크기**(로고 소형화 등)는 이미지 패널 '크기' **텍스트 필드 입력** — 슬라이더 드래그·`block.style.width` mutate ❌.
- [ ] 비율(원본/1:1/가로/세로)·정렬 = 패널 칩 fiber onClick.
- [ ] **시안과 다른 이미지는 Figma 노드에서 3배수(3x) scale로 직접 export**한 파일로 교체(해상도 확보) — 로고 등 투명 필요 자산은 `download_assets` export URL(배경 합성으로 둥근 모서리 밖에 페이지색 박힘) 대신 **노드 자체 export → rawImages 경로**로 투명 보존(2026-07-07 5025: 로고·예배당·목사 이미지 시안과 상이 → 재export·교체).
- [ ] **이미 채워진 이미지 카드/프로필 교체 ≠ 빈 카드 업로드** (2026-07-07 5025) — 채워진 카드엔 인라인 '이미지 업로드하기' 버튼이 없어 `openImageUpload(index)` 레시피 무효. → **프리뷰 이미지 위 38×38 오버레이 편집 버튼의 fiber onClick 직접 호출**(이미지 카드 `()=>{j("content")}` · 프로필 아바타 `()=>{p&&h("content")}`; 호버 숨김이라 rect=0이어도 fiber 호출은 무관). 여러 카드는 조상 fiber `block.id`로 디스앰비규에이트. 업로드 **파일명 고유하게**(라이브러리 alt=확장자없는 파일명 → 동명 시 `applyImage` 오매칭). 큰 base64(≥1MB)는 `$B js` 인자 한계 → `window.__cdbdImg="…"` JS 파일 `$B eval`(출력 폭주 방지 `>/dev/null`).
- [ ] **사용자 사전 업로드 흐름 (2026-07-07 워크플로 변경)** — 이미지를 사용자가 라이브러리에 미리 올려두면, S4는 업로드(base64·onDrop) 단계 **생략** → **라이브러리에서 `applyImage`(선택→적용)만**(파일명 부분일치). 업로드가 S4 최대 병목이라 이 경우 장당 수초로 급감. 라이브러리에 없을 때만 업로드 레시피 사용.

## ⚠️ 자동화 함정 — 파일 업로드

> 코드 레시피: skill `cdbd-card-automation`.

- [ ] **transient `<input type=file>` 후킹 ❌ → React `onDrop` 직접 호출** (함정23) — Bash `base64` → `$B js` inject → File 객체 → dropzone(`div.border-dashed` 또는 fiber `onDrop` 보유 div)의 `props.onDrop({preventDefault, stopPropagation, dataTransfer, target, currentTarget})` 직접 호출(`dt=new DataTransfer(); dt.items.add(file)`).
- [ ] 적용/저장도 동일 패턴 — 카드 `적용하기` → 모달 `저장하기` 각 `props.onClick` 직접 호출. 파일 ≤10MB 권장.
