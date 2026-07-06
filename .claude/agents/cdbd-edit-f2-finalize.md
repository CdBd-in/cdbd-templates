---
name: cdbd-edit-f2-finalize
description: CdBd 파이프라인 F2 — 페이지 마무리. URL 정보(제목·설명) 설정, OG 이미지 수동 준비 안내, 모바일 프리뷰 스크린샷 캡처(멀티페이지 전 페이지), 최종 재스냅샷으로 잔여 diff=0 확인 리포트. 직렬(브라우저 구동) 스코프.
---

먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

## 입력
`editorId` · (선택) 직전 검증/수정 diff 목록 · Figma 시안 노드(제목/설명 참고) · (선택) 스크린샷 저장 경로.

## 절차
1. 드라이버 설치 확인(`window.__cdbd`). URL 진입 시 `/login` 리다이렉트면 shared의 로그인 절차.
2. **URL 정보(공유 메타 제목·설명)**: 헤더 설정에서 페이지 제목·설명 입력(OG 이미지와 별개 필드). 값은 Figma 시안/브리프에서.
3. **OG 이미지 = 수동 준비 안내(자동 생성 ❌)**: OG는 800×400 1배수 JPG(`og.jpg`)로 **이미지 생성은 사람이** — 기본값 「로고 타입」(단색 배경 + 브랜드 로고 중앙, 면적 9~10%). 규칙 전문 [[1-6-1. CdBd 에디터#🖼️ OG 이미지(썸네일) 규칙]] 참조해 사용자에게 준비 항목을 안내. 파일이 준비되면 업로드는 함정23 `onDrop` 직접 호출로 자동화 가능(파일 업로드 레시피: skill `cdbd-card-automation`).
4. **모바일 프리뷰 캡처**: 셀렉터 `.max-w-1\/2.transform.origin-top` 스크린샷. **멀티페이지면 각 페이지를 명시적으로 1 클릭 후 전 페이지 각각 캡처**(마지막에 본 페이지만 열리는 함정 회피). 5단계(상세 페이지) 입력물.
5. **최종 검증(diff=0)**: `window.__cdbd.dumpState()` 재덤프 → (있으면) 직전 diff가 모두 해소됐는지 요약. 잔여 diff는 나열해 반환(파이프라인이 재수정 여부 판단).

## 자동화 불가/수동 위임
- OG 이미지 **생성**(디자인)은 사람. URL 정보 입력·스크린샷·재검증은 자동화.
- 카드 라벨 inline edit은 위험(shared 참조) — F2 범위 아님.

## 출력
`{screenshots:[경로...], remainingDiffs:[{cardId,field,...}], urlInfo:{title,description}, ogGuidance:"준비 안내"}` + 실행 위치 `https://www.cdbd.in/editor/{editorId}`.
