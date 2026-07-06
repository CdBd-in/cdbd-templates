# CdBd 에디터 서브에이전트 파이프라인 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 4단계(CdBd 에디터 구현)를 13개 스코프 서브에이전트 + 얇은 Workflow로 분할해, Figma 시안을 CdBd 에디터에 생성→검증→수정까지 자동화한다.

**Architecture:** 하이브리드 — 13개 재사용 스코프 에이전트(`.claude/agents/cdbd-edit-*.md`) + 결정론적 오케스트레이터(`.claude/workflows/cdbd-editor-pipeline.js`). 직렬 단계(S/F)만 브라우저를 구동하고, 병렬 검증(V1~V5)은 스냅샷 데이터 파일만 분석해 단일 세션 충돌을 원천 차단한다. 검증은 속성별(diff 산출), 수정은 카드별(diff를 카드ID로 묶어 적용).

**Tech Stack:** Claude Code 서브에이전트(`.claude/agents`), Workflow 툴(JS), gstack `browse`(`$B`), `window.__cdbd` 드라이버(`.claude/skills/cdbd-card-automation/card-driver.js`), Figma MCP(`get_design_context`), skill `cdbd-card-automation`.

**정본 스펙:** [[1-6-1. CdBd 에디터#🤖 4단계 서브에이전트 파이프라인 (생성→검증→수정 자동화)]] — 각 스코프 정의·매핑·완료기준의 출처.

## Global Constraints

- **단일 세션 규칙(E1)**: 직렬 단계(S1·S2·S3·S4·S5·S6·F1·F2)만 브라우저 접근. 병렬 V1~V5는 스냅샷 파일만 읽고 **브라우저·Figma 라이브 접근 금지**.
- **의존 순서(E2)**: Phase 1(토대) → 2(채움) → 스냅샷 → 3(검증) → 카드별 그룹핑 → 4(수정·마무리). 순서 고정.
- **보드 스크롤 금지**: 카드 선택은 fiber `onClick`(`D(m.id)`). 스크롤은 페이지 드리프트 유발.
- **예약 크레딧**: S6는 크레딧 있는 계정에서만 최종 완료. 부족 시 **부분완료 리포트**(파이프라인 중단 ❌).
- **diff 스키마(고정 8필드)**: `cardId, cardType, scope, field, current, expected, howToFix, severity(high|medium|low)`.
- **카드 라벨**: 목적·내용 이름 (기본 타입명 ❌).
- **색상**: 테마 변수 그대로(`{배경색}`/`{텍스트색}`/`{버튼색}`), 버튼 텍스트 = `{배경색}`.
- **커밋 정책(사용자 규칙)**: git 커밋·푸시는 **사용자가 요청할 때만**. 기본 브랜치면 먼저 브랜치. 아래 각 Task의 "Commit" 스텝은 사용자가 커밋하기로 한 경우에만 실행.
- **에이전트 파일 포맷**: `.claude/agents/*.md` = frontmatter(`name`·`description`) + 본문(시스템 프롬프트). 각 에이전트 본문은 (a) skill `cdbd-card-automation` 사용 지시, (b) 자기 스코프 정의(스펙에서 인라인), (c) 자기검증 스텝을 포함.

---

## 진행 상황 (2026-07-06 체크포인트)

**T1~T15 완료** (editor 5025). 코어 루프(T1~T3) + 전체 13 에이전트 + 오케스트레이터 빌드. 남은 것 **T16 파일럿**(⚠️ 세션 리로드 후 실행).
- **T1 ✅** `dumpState()` 드라이버 추가 — 17/17 캡처·순서보존·읽기전용.
- **T2 ✅** `.claude/cdbd-edit-shared.md` + `.claude/workflows/cdbd-editor-pipeline.js`(스텁+스키마).
- **T3 ✅** `cdbd-edit-v1-textdesign` + `cdbd-edit-f1-fix` + 코어 루프(스냅샷→검증→수정→**영속화**) 증명.
- **🔑 F1 영속화 정답**: block 참조 mutate → **`reorderCard` 라운드트립 commit**(autosave). 정렬버튼·패널 트리거는 커밋 안 됨(검증). `blockById` 드라이버 추가. 상세·부수발견(텍스트 디자인 2곳 저장): [[1-6-1. CdBd 에디터#🧪 파일럿 검증 (2026-07-06, editor 5025)]].
- **T4~T14 ✅** 13 에이전트 전부 생성: S1~S6(생성)·V1~V5(검증)·F1·F2. V2~V5는 5025 스냅샷 라이브 테스트 통과(비텍스트 diff 20건). S1~S6·F2는 파일 완성(라이브 검증은 파일럿).
- **T15 ✅** 오케스트레이터 완성(`.claude/workflows/cdbd-editor-pipeline.js`) — `mode`(full/verify/fix)·cardId+field 디둡·figmaFileKey. 본문 문법 검증 OK.
- **🔑 학습(2026-07-06 2세션)**: ①**신규 에이전트는 세션 리로드 전 `agentType` 미해결** → 오케스트레이터 실행 전 리로드 필수(우회: general-purpose에 `.md` 스펙 읽힘). ②**V3↔V5 버튼 borderRadius 중복 검출** → 디둡으로 해결. ③5025 전체 검증 = 50 diff(V1 30 + 비텍스트 20).
- **다음(T16)**: **세션 리로드 후** `Workflow({name:'cdbd-editor-pipeline', args:{editorId, figmaFileKey, figmaNodeId, mode}})`. 5025 재현=`mode:'verify'`(figmaFileKey `2CX6W3Zg9OzbBiwIZ9Tk6J`·node `8-3425`), 신규 원페이지=`mode:'full'`(S6 예약은 크레딧 필요).

---

### Task 1: 스냅샷 능력 확보 (`dumpState` 드라이버 메서드)

병렬 검증의 전제 = 한 번의 덤프로 전체 블록 JSON을 파일에 저장. 기존 `window.__cdbd.blocks()`가 `style`·`content`·`reservation`·`location`·`multiCard`까지 담는지 확인하고, 부족하면 `dumpState()`를 추가한다.

**Files:**
- Modify: `.claude/skills/cdbd-card-automation/card-driver.js` (`window.__cdbd`에 `dumpState` 추가)
- Test(수동): 스크래치 에디터 1개 (빈 페이지로 시작 → id를 `$TEST_EDITOR`로 기록)

**Interfaces:**
- Produces: `window.__cdbd.dumpState()` → `{ blocks: [{id,type,title,style,content,image,gallery,profile,divider,multiCard,location,reservation,...}], theme:{background,color,button}, font, buttonShape }` (마운트 여부 무관 전체 블록. 가상화로 `blocks()`가 일부만 반환하면 store에서 직접 회수).

- [ ] **Step 1: 현재 `blocks()` 반환 구조 실측**

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"
DRV=".claude/skills/cdbd-card-automation/card-driver.js"
$B goto https://www.cdbd.in/editor/$TEST_EDITOR; sleep 4
$B eval "$DRV"
$B js "JSON.stringify(window.__cdbd.blocks()[0]).slice(0,800)"   # 첫 블록 필드 확인
```
Expected: 블록 객체에 `id`·`type`·`style` 등이 보임. `content`/`reservation` 등 누락 여부 기록.

- [ ] **Step 2: `dumpState` 추가 (누락 필드가 있을 때만)**

`card-driver.js`의 `window.__cdbd` 객체에 아래 메서드를 추가. store(블록 배열 setter가 참조하는 React state)에서 전체 블록을 회수한다. 구현 시 기존 `blocks()`가 쓰는 fiber 경로를 재사용:

```js
// window.__cdbd 정의 블록 내부에 추가
dumpState: function () {
  var rows = this.boardRows();
  var blocks = rows.map(function (r) { return window.__cdbd.blockOfRow(r); }).filter(Boolean);
  // 가상화로 rows가 일부면, 미리보기 보드 fiber의 blocks prop을 우선 사용
  var full = (window.__cdbd._blocksFromStore && window.__cdbd._blocksFromStore()) || blocks;
  return {
    blocks: full,
    theme: (window.__cdbd.themeColors && window.__cdbd.themeColors()) || null
  };
},
```
누락이 없으면 이 Task는 "확인만"으로 종료(파일 수정 없음).

- [ ] **Step 3: 전체 덤프가 카드 수와 일치하는지 검증**

```bash
$B js "var s=window.__cdbd.dumpState(); JSON.stringify({n:s.blocks.length, types:s.blocks.map(b=>b.type)})"
```
Expected: `n` = 카드 보드 실제 카드 수와 일치, 모든 카드 타입 나열.

- [ ] **Step 4: Commit (사용자 커밋 정책에 따름)**

```bash
git add ".claude/skills/cdbd-card-automation/card-driver.js"
git commit -m "feat(cdbd): add dumpState() for full-block snapshot"
```

---

### Task 2: 공유 계약 — diff 스키마 + 에이전트 템플릿

모든 에이전트가 참조할 공통 계약을 확정한다. diff 스키마는 워크플로에 상수로, 에이전트 공통 본문은 템플릿 파일로 둔다.

**Files:**
- Create: `.claude/cdbd-edit-shared.md` (에이전트 공통 지침 — `agents/` 밖에 둬서 에이전트 로더가 파싱하지 않게. 각 에이전트가 "먼저 읽기"로 참조)
- Create: `.claude/workflows/cdbd-editor-pipeline.js` (지금은 `meta` + `DIFF_SCHEMA` 상수까지만; 오케스트레이션은 Task 15)

**Interfaces:**
- Produces: `DIFF_SCHEMA`(JSON Schema, 8필드), `_cdbd-edit-shared.md`(공통 규칙 텍스트).

- [ ] **Step 1: 공통 레퍼런스 작성**

`.claude/cdbd-edit-shared.md`:
```markdown
# cdbd-edit 공통 지침 (모든 스코프 에이전트가 먼저 읽는다)

- 정본 스펙: `1. 작업 가이드/1-5-1. CdBd 에디터.md`의 "🤖 4단계 서브에이전트 파이프라인" 섹션.
- 자동화: skill `cdbd-card-automation` 사용. 브라우저는 gstack `browse`(`$B`), 드라이버는 `window.__cdbd`.
- 단일 세션: 직렬 스코프(S*/F*)만 브라우저 구동. 검증 스코프(V*)는 스냅샷 파일만 읽고 브라우저 접근 금지.
- 카드 선택은 fiber onClick(보드 스크롤 금지). 색상은 테마 변수, 버튼 텍스트=배경색, 카드 라벨=목적 이름.
- diff 8필드: cardId, cardType, scope, field, current, expected, howToFix, severity(high|medium|low).
- 완료 보고에 실행 위치(editor URL) 포함.
```

- [ ] **Step 2: 워크플로 파일 스텁 + 스키마 상수**

`.claude/workflows/cdbd-editor-pipeline.js`:
```js
export const meta = {
  name: 'cdbd-editor-pipeline',
  description: 'CdBd 4단계: Figma 시안을 CdBd 에디터에 생성→검증→수정 (13 스코프)',
  phases: [{ title: '토대' }, { title: '채움' }, { title: '검증' }, { title: '수정·마무리' }],
}
const DIFF_SCHEMA = {
  type: 'object', required: ['diffs'],
  properties: { diffs: { type: 'array', items: {
    type: 'object',
    required: ['cardId','cardType','scope','field','current','expected','howToFix','severity'],
    properties: {
      cardId:{type:'string'}, cardType:{type:'string'}, scope:{type:'string'},
      field:{type:'string'}, current:{type:'string'}, expected:{type:'string'},
      howToFix:{type:'string'}, severity:{type:'string', enum:['high','medium','low']},
    } } } },
}
log('cdbd-editor-pipeline: 스텁 (Task 15에서 완성)')
return { stub: true }
```

- [ ] **Step 3: 워크플로 스텁이 파싱·실행되는지 확인**

Run: `Workflow({ scriptPath: ".claude/workflows/cdbd-editor-pipeline.js" })`
Expected: 에러 없이 `{ stub: true }` 반환 (meta 파싱 OK).

- [ ] **Step 4: Commit (사용자 커밋 정책에 따름)**

```bash
git add ".claude/cdbd-edit-shared.md" ".claude/workflows/cdbd-editor-pipeline.js"
git commit -m "feat(cdbd): add diff schema + shared agent reference"
```

---

### Task 3: 수직 슬라이스 — V1(텍스트 디자인) + F1(수정) 코어 루프 증명

전체 13개를 만들기 전에 **스냅샷 → 검증 → 수정** 루프를 최소 스코프로 증명한다. `$TEST_EDITOR`에 텍스트 카드 1개를 두고 폰트 크기를 일부러 틀리게 심은 뒤, V1이 diff를 잡고 F1이 고치는지 확인.

**Files:**
- Create: `.claude/agents/cdbd-edit-v1-textdesign.md`
- Create: `.claude/agents/cdbd-edit-f1-fix.md`

**Interfaces:**
- Consumes: `dumpState()`(Task 1), `DIFF_SCHEMA`(Task 2).
- Produces: V1 = `{diffs:[...]}` (스키마 준수). F1 = 카드ID의 diff 배열을 받아 적용 후 `{applied, remaining}`.

- [ ] **Step 1: V1 에이전트 파일 작성**

`.claude/agents/cdbd-edit-v1-textdesign.md`:
```markdown
---
name: cdbd-edit-v1-textdesign
description: CdBd 파이프라인 V1 — 스냅샷 파일과 Figma 스펙을 비교해 텍스트 "디자인"(폰트·사이즈·웨이트·색·줄간격·정렬) 불일치를 diff로 산출. 읽기 전용, 브라우저 접근 금지. 줄바꿈(위치)은 S3 소관이라 제외.
---
먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

역할: 입력으로 받은 스냅샷 JSON 파일 경로(CdBd blocks + Figma spec)를 열어, 텍스트가 있는 모든 카드의 **디자인 속성만** 비교한다:
- 폰트(서체), 사이즈(px), 웨이트(Bold on/off), 색(hex/rgba), 줄간격(lineHeight 1.2~2.0), 정렬(left/center/right).
- 줄바꿈 위치는 **비교하지 않는다**(S3 소관).
CdBd 값은 `block.style`(fontSize·color·lineHeight·textAlign)과 Bold 토글에서, 기대값은 Figma 텍스트 노드에서 읽는다.
브라우저·Figma 라이브 접근 금지 — **스냅샷 파일만** 사용.
출력: diff 리스트(스키마 8필드). 불일치 없으면 `{diffs:[]}`.
howToFix 예: "block.style.fontSize=24 후 정렬버튼 .click()로 트리거".
```

- [ ] **Step 2: F1 에이전트 파일 작성**

`.claude/agents/cdbd-edit-f1-fix.md`:
```markdown
---
name: cdbd-edit-f1-fix
description: CdBd 파이프라인 F1 — 한 카드(cardId)에 대한 diff 배열을 받아 CdBd 에디터에서 실제 수정. 카드 1회 선택 후 그 카드의 모든 diff를 적용하고 재확인.
---
먼저 `.claude/cdbd-edit-shared.md`를 읽는다.

입력: editorId, cardId, 그 카드의 diff 배열(각 diff의 field/expected/howToFix 포함).
절차:
1) `window.__cdbd` 설치 확인. 카드 선택은 fiber onClick(보드 스크롤 금지).
2) diff마다 howToFix대로 적용. 텍스트 스타일은 `block.style` 직접 변경 + 트리거(정렬버튼 .click() 등), 비텍스트는 다른 패널 변경으로 store update 유발 (스펙/skill 참조).
3) 적용 후 `dumpState()` 재덤프 → 해당 diff 해소 확인. 미해소는 재시도(≤2).
출력: `{cardId, applied:[field...], remaining:[field...]}`. 실행 editor URL 포함.
```

- [ ] **Step 3: 실패 조건 심기 (seeded mismatch)**

```bash
# $TEST_EDITOR에 텍스트 카드 1개 확보(없으면 복제), 폰트 크기를 Figma와 다르게 심음
$B goto https://www.cdbd.in/editor/$TEST_EDITOR; sleep 4; $B eval "$DRV"
$B js "var b=window.__cdbd.dumpState().blocks.find(x=>x.type==='text'); JSON.stringify(b.style)"  # 현재값 기록
# 스냅샷 파일 생성: cdbd 덤프 + (테스트용) figma 기대 fontSize를 다르게 명시
$B js "var s=window.__cdbd.dumpState(); s.figmaExpect={textFontSize:24}; require&&0; JSON.stringify(s)" > /tmp/cdbd-snap-test.json
```
Expected: `/tmp/cdbd-snap-test.json`에 현재 fontSize(예: 16)와 figmaExpect 24가 함께 존재.

- [ ] **Step 4: V1 디스패치 → diff 확인**

Run(Agent 툴): `subagent_type: cdbd-edit-v1-textdesign`, 프롬프트 = "스냅샷 `/tmp/cdbd-snap-test.json` 비교, 텍스트 디자인 diff 산출."
Expected: `diffs`에 `field:"fontSize"`, `current:"16"`, `expected:"24"` 항목 1개 (스키마 8필드 충족).

- [ ] **Step 5: F1 디스패치 → 수정 확인**

Run(Agent 툴): `subagent_type: cdbd-edit-f1-fix`, 프롬프트 = "editor `$TEST_EDITOR`, cardId `<위 diff의 cardId>`, diff `<Step4 결과>` 적용."
그다음:
```bash
$B js "var b=window.__cdbd.dumpState().blocks.find(x=>x.type==='text'); b.style.fontSize"
```
Expected: fontSize = 24 (F1이 적용). 코어 루프 증명 완료.

- [ ] **Step 6: Commit (사용자 커밋 정책에 따름)**

```bash
git add ".claude/agents/cdbd-edit-v1-textdesign.md" ".claude/agents/cdbd-edit-f1-fix.md"
git commit -m "feat(cdbd): V1 text-design verify + F1 card fix (core loop)"
```

---

### Task 4: S1 페이지 토대 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-s1-foundation.md`

**Interfaces:** Consumes: editorId, figmaNodeId. Produces: 테마 적용된 빈 페이지(들).

- [ ] **Step 1: 파일 작성** — frontmatter `name: cdbd-edit-s1-foundation` / `description`(전역 테마·서체·버튼모양·페이지배경·제목·스크롤애니메이션·멀티페이지 목록 설정). 본문: `_cdbd-edit-shared.md` 읽기 지시 + 스코프 정의(담당/입력/출력/자기검증 — 스펙 S1 블록 인라인) + `setThemeColor` 재조정 루프·경고모달 처리.
- [ ] **Step 2: 검증** — `$TEST_EDITOR`에 디스패치 → `$B js "JSON.stringify(window.__cdbd.themeColors())"`로 3색 일치 확인. Expected: 지정 hex 3색 일치.
- [ ] **Step 3: Commit (정책에 따름)** — `git add .claude/agents/cdbd-edit-s1-foundation.md && git commit -m "feat(cdbd): S1 page-foundation agent"`

---

### Task 5: S2 카드 구성 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-s2-cards.md`

**Interfaces:** Consumes: Figma 카드 매니페스트(타입·순서·라벨). Produces: 올바른 순서·라벨의 빈 카드 스택.

- [ ] **Step 1: 파일 작성** — `description`(15종 add·순서·상하고정·카드명). 본문: 공통 읽기 + S2 스코프 인라인 + `openAddModal`/`pickCardType`/`reorderCard`/`openPin`/`setTitle` 수렴루프·예약 크레딧 확인.
- [ ] **Step 2: 검증** — 스크래치 에디터에 "텍스트→이미지→버튼" 3카드 매니페스트 디스패치 → `$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"`. Expected: `["text","image","button"]`. 라벨 `firstBad()===-1`.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): S2 card-composition agent"`

---

### Task 6: S3 텍스트 내용 에이전트 (줄바꿈 포함)

**Files:** Create: `.claude/agents/cdbd-edit-s3-text.md`

**Interfaces:** Consumes: 카드별 텍스트(정확한 문자열·개행). Produces: 텍스트 채워진 카드 + 줄바꿈 일치.

- [ ] **Step 1: 파일 작성** — `description`(모든 텍스트 필드 채움+버튼텍스트+줄바꿈 대조). 본문: 공통 읽기 + S3 스코프 인라인(대상 필드 목록) + "텍스트=복제 후 Lexical" + 자기검증(`block.content` JSON.parse → linebreak 노드 위치가 Figma 줄 구조와 일치). "줄바꿈=내용(S3), 줄간격=디자인(V1)" 명시.
- [ ] **Step 2: 검증** — 2줄짜리 텍스트를 심고 디스패치 → `$B js "JSON.parse(window.__cdbd.dumpState().blocks.find(b=>b.type==='text').content)"`에서 linebreak 노드 존재·위치 확인. Expected: Figma 지정 위치에서 개행.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): S3 text-content agent (incl. line breaks)"`

---

### Task 7: S4 이미지 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-s4-image.md`

**Interfaces:** Consumes: 준비된 이미지 파일 + 슬롯↔이미지 매핑. Produces: 이미지 적용된 카드(순서 일치).

- [ ] **Step 1: 파일 작성** — `description`(모든 이미지 슬롯 업로드·적용·순서 + 카드/레이어 배경이미지). 본문: 공통 읽기 + S4 스코프 인라인 + `openImageUpload`/`uploadImage`/`applyImage`. 사이즈·모양은 V2 소관 명시.
- [ ] **Step 2: 검증** — 이미지 카드 1개에 테스트 이미지 디스패치 → 스크린샷으로 표시 확인 + `dumpState()`에서 image 참조 존재. Expected: 카드에 이미지 렌더.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): S4 image agent"`

---

### Task 8: S5 링크·기능 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-s5-link.md`

**Interfaces:** Consumes: 링크·폼·채널 정의. Produces: 동작하는 링크·폼·임베드.

- [ ] **Step 1: 파일 작성** — `description`(링크 6종·위치 지오코딩·Q&A 폼·유튜브·SNS). 본문: 공통 읽기 + S5 스코프 인라인 + `onUpdateItem`(전화=`type:'call'`)·위치 지오코딩(검색 선택 필수) 처리.
- [ ] **Step 2: 검증** — 버튼 카드에 전화링크 디스패치 → `dumpState()`에서 `linkButton.type==='call'` & `href` 확인. 위치 카드 지오코딩 → `location.lat/lng/naverMapsUrl` 존재. Expected: 값 존재.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): S5 link/function agent"`

---

### Task 9: S6 예약 정보 에이전트 (부분완료 처리)

**Files:** Create: `.claude/agents/cdbd-edit-s6-reservation.md`

**Interfaces:** Consumes: 예약 일정·정원. Produces: 저장된 예약 정보 또는 부분완료 리포트.

- [ ] **Step 1: 파일 작성** — `description`(날짜·시간·정원·방문체크 종료 필수·크레딧). 본문: 공통 읽기 + S6 스코프 인라인 + 예약 정보 모달 절차(방문체크 종료 필수) + **크레딧 부족 시 리포트 반환하고 파이프라인 중단 금지**.
- [ ] **Step 2: 검증** — 예약 카드에 날짜/시간/정원/방문체크종료 디스패치 → 모달 닫힘=저장, 우측 패널 예약정보 표시 확인. 크레딧 0이면 `{status:'partial', reason:'credit'}` 반환 확인. Expected: 저장 또는 명시적 부분완료.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): S6 reservation agent (partial-aware)"`

---

### Task 10: V2 이미지·모양 검증 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-v2-imageshape.md`

**Interfaces:** Consumes: 스냅샷 파일. Produces: `{diffs}`(스키마).

- [ ] **Step 1: 파일 작성** — Task 3의 V1 파일을 **템플릿으로** 하되 스코프만 교체: 이미지 비율(원본/1:1/3:2/2:3)·모양(8종)·크기, 갤러리 이미지 모서리, 프로필 이미지 비율·크기·모양. 읽기 전용·브라우저 금지 문구 유지.
- [ ] **Step 2: 검증** — 이미지 모서리를 Figma와 다르게 심은 스냅샷으로 디스패치 → diff에 `field:"borderRadius"` 산출 확인(스키마 충족).
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): V2 image-shape verify agent"`

---

### Task 11: V3 버튼·구분선 검증 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-v3-button-divider.md`

- [ ] **Step 1: 파일 작성** — V1 템플릿, 스코프: 버튼 가로(1~10)·세로(1~10)·모양 + 구분선 두께·모양(실선/대시/점선/물결)·색·상하여백.
- [ ] **Step 2: 검증** — 구분선 두께를 다르게 심은 스냅샷 → diff `field:"strokeWidth"` 산출 확인.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): V3 button/divider verify agent"`

---

### Task 12: V4 레이아웃 유형 검증 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-v4-layout.md`

- [ ] **Step 1: 파일 작성** — V1 템플릿, 스코프: 프로필(기본형/강조형/명함형)·갤러리(나열/넘겨보기/그리드+단수·간격·자동넘김)·메뉴(한눈에/햄버거+프리셋)·버튼 이미지유형·상품(그리드/바)·Q&A(정렬·질문간격)·2단(2~4분할·비율·정렬).
- [ ] **Step 2: 검증** — 갤러리 유형을 다르게 심은 스냅샷 → diff `field:"galleryType"`(또는 `gridColumn`) 산출 확인.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): V4 layout verify agent"`

---

### Task 13: V5 카드 디자인 검증 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-v5-carddesign.md`

- [ ] **Step 1: 파일 작성** — V1 템플릿, 스코프: 배경(색/이미지+필터)·테두리(색+두께)·모서리·내부여백·외부여백 + 레이어 배치(크기·X·Y).
- [ ] **Step 2: 검증** — 내부여백을 다르게 심은 스냅샷 → diff `field:"padding"` 산출 확인.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): V5 card-design verify agent"`

---

### Task 14: F2 마무리 에이전트

**Files:** Create: `.claude/agents/cdbd-edit-f2-finalize.md`

**Interfaces:** Consumes: editorId, 최종 스냅샷. Produces: 모바일 프리뷰 스크린샷 + 최종 diff=0 리포트.

- [ ] **Step 1: 파일 작성** — `description`(OG 수동안내·URL정보 제목/설명·모바일 캡처·최종 diff=0). 본문: 공통 읽기 + F2 스코프 인라인 + 셀렉터 `.max-w-1\/2.transform.origin-top` 캡처(멀티=전 페이지) + OG는 자동화 불가라 수동 준비 안내.
- [ ] **Step 2: 검증** — `$TEST_EDITOR`에 디스패치 → 모바일 프리뷰 스크린샷 생성 확인 + 재스냅샷 diff 요약 반환. Expected: 스크린샷 파일 생성.
- [ ] **Step 3: Commit (정책에 따름)** — `git commit -m "feat(cdbd): F2 finalize agent"`

---

### Task 15: Workflow 오케스트레이터 완성

Task 2의 스텁을 실제 파이프라인으로 완성한다. 직렬 S/F는 각 `agentType`으로, 스냅샷은 전용 직렬 agent가 파일로 저장, 병렬 V는 그 파일만 읽음, 수정은 카드ID 그룹핑 후 직렬 F1.

**Files:** Modify: `.claude/workflows/cdbd-editor-pipeline.js`

**Interfaces:** Consumes: `args = { editorId, figmaNodeId }`, 13개 에이전트(Task 3~14). Produces: `{ diffCount, reservation, screenshots }`.

- [ ] **Step 1: 오케스트레이션 본문 작성 (스텁 `log/return` 교체)**

```js
const { editorId, figmaNodeId } = args

phase('토대')
await agent(`editor ${editorId}, figma ${figmaNodeId}: 페이지 테마·서체·버튼모양·페이지배경·제목·애니메이션 설정.`, {agentType:'cdbd-edit-s1-foundation', label:'S1 토대'})
await agent(`editor ${editorId}, figma ${figmaNodeId}: 카드 추가·순서·고정·라벨.`, {agentType:'cdbd-edit-s2-cards', label:'S2 구성'})

phase('채움')
await agent(`editor ${editorId}, figma ${figmaNodeId}: 모든 텍스트+버튼텍스트+줄바꿈 채움.`, {agentType:'cdbd-edit-s3-text', label:'S3 텍스트'})
await agent(`editor ${editorId}, figma ${figmaNodeId}: 모든 이미지 슬롯 업로드·적용(순서).`, {agentType:'cdbd-edit-s4-image', label:'S4 이미지'})
await agent(`editor ${editorId}, figma ${figmaNodeId}: 링크·지오코딩·Q&A폼·유튜브·SNS.`, {agentType:'cdbd-edit-s5-link', label:'S5 링크'})
const reservation = await agent(`editor ${editorId}: 예약 날짜·시간·정원·방문체크. 크레딧 부족 시 부분완료 리포트.`, {agentType:'cdbd-edit-s6-reservation', label:'S6 예약'})

// 스냅샷 1회 (직렬) — cdbd dumpState + figma spec을 /tmp에 저장, 경로 반환
const snapPath = await agent(`editor ${editorId} window.__cdbd.dumpState()와 figma ${figmaNodeId} get_design_context를 /tmp/cdbd-snap-${editorId}.json에 병합 저장. 파일 경로만 반환.`, {label:'스냅샷'})

phase('검증')
const V = ['v1-textdesign','v2-imageshape','v3-button-divider','v4-layout','v5-carddesign']
const reviews = await parallel(V.map(v => () =>
  agent(`스냅샷 파일 ${snapPath} 만 읽어 ${v} 스코프 diff 산출. 브라우저·Figma 라이브 접근 금지.`,
    {agentType:`cdbd-edit-${v}`, schema:DIFF_SCHEMA, label:v, phase:'검증'})))
const diffs = reviews.filter(Boolean).flatMap(r => r.diffs)

// 카드ID로 그룹핑
const byCard = {}
for (const d of diffs) { (byCard[d.cardId] ||= []).push(d) }

phase('수정·마무리')
for (const cardId of Object.keys(byCard)) {
  await agent(`editor ${editorId}, 카드 ${cardId} diff 적용: ${JSON.stringify(byCard[cardId])}`,
    {agentType:'cdbd-edit-f1-fix', label:`F1 ${cardId.slice(0,6)}`})
}
const screenshots = await agent(`editor ${editorId} 마무리: OG 수동안내·URL정보·모바일 캡처·재스냅샷 diff=0 확인.`, {agentType:'cdbd-edit-f2-finalize', label:'F2 마무리'})

return { diffCount: diffs.length, reservation, screenshots }
```

- [ ] **Step 2: 드라이런 (스코프 축소로 흐름 검증)**

Run: `Workflow({ scriptPath: ".claude/workflows/cdbd-editor-pipeline.js", args: { editorId: "$TEST_EDITOR", figmaNodeId: "<테스트 노드>" } })`
Expected: 4 phase가 순서대로 진행, 검증 5개가 /workflows에서 **동시(병렬)** 표시, 카드별 F1 루프 실행, `{diffCount,...}` 반환. (테스트 에디터라 diff 소수)

- [ ] **Step 3: 단일 세션 위반 없음 확인**

`/workflows` 라이브 로그에서 V1~V5가 브라우저를 열지 않고 스냅샷 파일만 읽는지 확인(로그에 `$B goto` 부재). Expected: V 단계에 브라우저 네비게이션 없음.

- [ ] **Step 4: Commit (사용자 커밋 정책에 따름)**

```bash
git add ".claude/workflows/cdbd-editor-pipeline.js"
git commit -m "feat(cdbd): complete editor-pipeline orchestrator"
```

---

### Task 16: 실템플릿 파일럿 + 문서 동기화

실제 신규 템플릿 1개(단순 원페이지)로 파이프라인 전체를 돌려 스코프 경계·retry를 튜닝하고, 스펙의 "다음 단계"대로 문서를 동기화한다.

**Files:**
- Modify: `1. 작업 가이드/1-5-1. CdBd 에디터.md` (파이프라인 섹션 "미해결" 갱신 + 파일럿 교훈)
- Modify: `CLAUDE.md` (4단계 섹션에서 이 파이프라인 참조 추가)
- Modify: `1. 작업 가이드/1-1. 워크플로우.md` (4단계에 파이프라인 링크)

**Interfaces:** Consumes: 완성된 워크플로(Task 15) + 실 Figma 시안.

- [ ] **Step 1: 파일럿 실행** — 단순 원페이지 신규 시안으로 `Workflow(... args:{editorId, figmaNodeId})` 실행. 최종 diff·부분완료·캡처 결과 기록.
- [ ] **Step 2: 튜닝** — 파일럿에서 드러난 스코프 누수·오탐(false diff)·retry 한계를 각 에이전트 파일에 반영(예: V가 테마 상속값을 diff로 오탐하면 "테마 변수 상속값은 diff 아님" 규칙 추가).
- [ ] **Step 3: 문서 동기화** — 1-5-1 파이프라인 섹션 "미해결·다음 단계" 체크박스 갱신 + 파일럿 교훈 1~2줄 추가. CLAUDE.md 4단계 섹션과 1-1 워크플로우 4단계에 `[[1-5-1. CdBd 에디터#🤖 4단계 서브에이전트 파이프라인 (생성→검증→수정 자동화)]]` 링크 추가.
- [ ] **Step 4: Commit (사용자 커밋 정책에 따름)** — `git commit -m "docs(cdbd): pilot learnings + pipeline doc sync"`

---

## Self-Review

**Spec coverage:** 13개 스코프(S1·S2 / S3·S4·S5·S6 / V1~V5 / F1·F2) 각각 Task 있음 — S1(T4)·S2(T5)·S3(T6)·S4(T7)·S5(T8)·S6(T9)·V1(T3)·V2(T10)·V3(T11)·V4(T12)·V5(T13)·F1(T3)·F2(T14). 스냅샷 메커니즘(T1)·diff 스키마(T2)·오케스트레이션(T15)·완료기준(T15 Step2-3, T16)·문서동기화(T16) 포함. 하이브리드 산출(A 13파일 + B 워크플로) 모두 커버.

**Placeholder scan:** 반복 V 에이전트(T10~T13)는 "V1을 템플릿으로 스코프 교체"라 명시하되 각 스코프 내용을 인라인으로 적어 out-of-order 독해 가능. 스코프 상세 원문은 정본 스펙(1-5-1) 참조 — 안정적 외부 문서라 placeholder 아님.

**Type consistency:** `dumpState()`(T1) → 모든 V·F가 소비. `DIFF_SCHEMA` 8필드(T2) → V 출력·F1 입력·워크플로 동일. `agentType` 문자열(`cdbd-edit-*`)이 파일 `name` frontmatter와 일치(T3~T14 ↔ T15). 일관.

---

## Execution Handoff

계획이 저장됨: `docs/superpowers/plans/2026-07-06-cdbd-editor-pipeline.md`.
