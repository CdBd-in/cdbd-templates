# cdbd-edit 공통 지침 (모든 스코프 에이전트가 먼저 읽는다)

- 정본 스펙: `1. 작업 가이드/1-6-1. CdBd 에디터.md`의 "🤖 4단계 서브에이전트 파이프라인" 섹션.
- 자동화: skill `cdbd-card-automation` 사용. 브라우저는 gstack `browse`(`$B`), 드라이버는 `window.__cdbd`(`.claude/skills/cdbd-card-automation/card-driver.js`).
- 단일 세션: 직렬 스코프(S*/F*)만 브라우저 구동. 검증 스코프(V*)는 **스냅샷 파일만** 읽고 브라우저·Figma 라이브 접근 금지.
- 카드 선택은 fiber onClick(보드 스크롤 금지 — 드리프트 유발). 색상은 테마 변수(`{배경색}`/`{텍스트색}`/`{버튼색}`), 버튼 텍스트 = `{배경색}`, 카드 라벨 = 목적·내용 이름.
- diff 8필드: `cardId, cardType, scope, field, current, expected, howToFix, severity(high|medium|low)`.
- 완료 보고에 실행 위치(editor URL `https://www.cdbd.in/editor/{id}`) 포함.
