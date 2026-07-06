---
name: cdbd-edit-s1-foundation
description: CdBd 파이프라인 S1 — 페이지 토대. 전역 테마 색(배경·텍스트·버튼 hex)·서체·버튼 모양(원형/각진/둥근)·페이지 배경·페이지 제목·스크롤 애니메이션·멀티페이지 목록 설정. 직렬(브라우저 구동).
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다. 자동화는 skill `cdbd-card-automation` 사용.

## 담당 (Figma 시안 → 페이지 전역 설정)
- **테마 3색**: 배경 `{배경색}`·텍스트 `{텍스트색}`·버튼 `{버튼색}` hex.
- **서체**: 페이지 기본 폰트(1~2개, 국문 본문 = 한글 폰트 의무).
- **버튼 모양**: 원형/각진/둥근 중 1.
- **페이지 배경·제목**: 배경색/이미지, 페이지 제목.
- **스크롤 애니메이션**: 위로/확대/없음.
- **멀티페이지**: 페이지 목록(표지+서브) 생성.

## 🔑 자동화 (skill 레시피)
- **페이지 색상**: swatch 클릭·hex input 없이 fiber `onChange("#hex")` 직접 호출. 슬롯은 onChange 소스로 식별(배경=`base.background`·텍스트=`base.color`·버튼=`button.background`, 위치 인덱스 ❌). **한 색씩 + 사이 재렌더 대기(~1.2s) + 배경을 마지막에**(핸들러가 stale state 캡처해 앞 변경 덮어씀). skill `cdbd-card-automation#페이지-색상`.
- **경고 모달**: 첫 테마 변경 시 「이 페이지에서 앞으로 경고 보지 않기」 체크 ON → 변경. 이후 안 뜸. 서체·버튼모양 변경도 같은 모달.
- **스크롤 애니메이션**: 헤더 💡 아이콘 → 모달(위로/확대/없음) → 저장.

## 자기검증
`$B js "JSON.stringify(window.__cdbd.themeColors())"` → 3색 일치. 안 맞으면 `onChange` 재조정 루프. 버튼 텍스트 = `{배경색}` 매핑·버튼-배경 대비 ≥3.6:1 확인.

## 출력
`{theme:{background,color,button}, font, buttonShape, pages:[...]}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
