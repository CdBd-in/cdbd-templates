# cdbd-edit 공통 지침 (모든 스코프 에이전트가 먼저 읽는다)

- 정본 스펙: `1. 작업 가이드/1-6-1. CdBd 에디터.md`의 "🤖 4단계 서브에이전트 파이프라인" 섹션.
- 자동화: skill `cdbd-card-automation` 사용. 브라우저는 gstack `browse`(`$B`), 드라이버는 `window.__cdbd`(`.claude/skills/cdbd-card-automation/card-driver.js`).
- 단일 세션: 직렬 스코프(S*/F*)만 브라우저 구동. 검증 스코프(V*)는 **스냅샷 파일만** 읽고 브라우저·Figma 라이브 접근 금지.
- 카드 선택은 fiber onClick(보드 스크롤 금지 — 드리프트 유발). 색상은 테마 변수(`{배경색}`/`{텍스트색}`/`{버튼색}`), 버튼 텍스트 = `{배경색}`, 카드 라벨 = 목적·내용 이름.
- diff 8필드: `cardId, cardType, scope, field, current, expected, howToFix, severity(high|medium|low)`.
- 완료 보고에 실행 위치(editor URL `https://www.cdbd.in/editor/{id}`) 포함.

## ⚠️ 영속화: block mutate로 되는 것 vs 패널 UI로만 되는 것 (2026-07-06 검증)
- **block mutate + reorder-commit으로 영속됨**: 텍스트 디자인(폰트·크기·색·정렬·줄간격 — `block.style` + `block.content` Lexical 둘 다)·줄바꿈(linebreak 노드)·모서리 `borderRadius`·배경 `background`·이미지 비율 `aspectRatio`·`multiCard.ratio`/`align`·`divider.*`.
- **block mutate로 리버트(리로드 원복) → 패널/프리뷰 UI로만 영속**:
  - **카드 외부여백/내부여백**(특히 multiCard·reservation): `block.style.margin/padding` mutate는 리버트. **패널 "카드 디자인" 여백 컨트롤 = [슬라이더 | 텍스트필드 | 우측 아코디언 버튼(chevron)]. 아코디언 버튼 onClick → 상/하/좌/우 개별 필드가 펼쳐져 방향성 설정 가능**(2026-07-06 정정 — '단일값·structural 불가'는 오류였음). 각 방향 텍스트 필드에 키보드 입력 → `block.style`에 CSS shorthand로 커밋·영속(예: `margin:'0px 20px'`=좌우20 인셋, `padding:'4px 20px 8px'`=상4·좌우20·하8). multiCard·reservation은 "카드 디자인"이 MuiCollapse라 헤더 먼저 펼치고 field `scrollIntoView` 후 click.
  - **예약 콘텐츠**(버튼 텍스트·날짜·정원): 예약 정보 모달 + 프리뷰 contenteditable로만.
  - **위치 label/button/address**: 위치 카드 패널 토글 + 검색 지오코딩으로만.
- **패널 컨트롤 영속 방법**: **🥇 슬라이더 우측에 텍스트 필드(number input)가 있으면 슬라이더 대신 그 필드에 실제 키보드 입력**(`$B click 필드 → Meta+a → $B type "값" → Enter`) — 더 정확·안정(2026-07-06 사용자 지침). 텍스트 필드 없는 슬라이더·토글·칩만 **React fiber 외부 onChange 직접 호출**(페이지 색상 방식). 이미지 업로드는 dropzone `onDrop`. 예약/버튼 텍스트는 **프리뷰 contenteditable 실제 키보드**(`$B click #id → Meta+a → $B type`; `execCommand('insertText')`는 Lexical에서 무반응 ❌). 토글 연속 조작은 fiber 재쿼리(stale-closure 회피).
