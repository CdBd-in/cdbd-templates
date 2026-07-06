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

## 자기검증
스크린샷으로 렌더 확인 + `dumpState()`에서 image 참조 존재.

## 출력
`{applied:[{cardId,slot}...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
