# cdbd-edit 공통 지침 (모든 스코프 에이전트가 먼저 읽는다)

- 파이프라인 요약: `1. 작업 가이드/1-6. CdBd 에디터·카드 기능.md` "🤖 4단계 서브에이전트 파이프라인" 절 · 설계 정본 = `docs/superpowers/plans/2026-07-06-cdbd-editor-pipeline.md` + 각 스코프 에이전트(`.claude/agents/editor-*.md`).
- 자동화: skill `cdbd-card-automation` 사용. 브라우저는 gstack `browse`(`$B`), 드라이버는 `window.__cdbd`(`.claude/skills/cdbd-card-automation/card-driver.js`).
- 단일 세션: 직렬 스코프(S*/F*)만 브라우저 구동. 검증 스코프(V*)는 **스냅샷 파일만** 읽고 브라우저·Figma 라이브 접근 금지.
- 카드 선택은 fiber onClick(보드 스크롤 금지 — 드리프트 유발). 색상은 테마 변수(`{배경색}`/`{텍스트색}`/`{버튼색}`), 버튼 텍스트 = `{배경색}`, 카드 라벨 = 목적·내용 이름.
- diff 8필드: `cardId, cardType, scope, field, current, expected, howToFix, severity(high|medium|low)`.
- 완료 보고에 실행 위치(editor URL `https://www.cdbd.in/editor/{id}`) 포함.

## 🔬 검증 스코프(V*) 공통 규칙 (2026-07-07 5025 미스 회고)

> 왜: 5025에서 로고 크기·예배당 둥근·2단 내부여백·비-legal 버튼/지도·좌우 여백 5건이 빠짐. 근본원인 4종을 절차로 차단.

- [ ] **A. 스펙은 카드×속성 전 매트릭스로 추출** — 사용자가 언급한 축만 보지 말 것. 스펙에 없는 속성은 diff가 조용히 빈 배열=거짓 '일치'가 됨(측정 안 한 건 검증 불가). 각 V는 대상 카드의 **모든 담당 속성을 빠짐없이** Figma 실측해 채운 뒤 비교. 이전 에디터 예시값을 이어받지 말고 **이번 시안 실측**.
- [ ] **B. 불일치 발견 = 반드시 diff 방출** — '확인'만 하고 넘기지 말 것. 읽기 전용 확인이 수정 필요를 찾고도 diff를 안 내면 F1이 못 고침(2026-07-07 예배당 '둥근' 유실 원인).
- [ ] **C. Figma-literal ❌ → CdBd-legal 스냅 비교** — borderRadius·비율·높이는 px 정확일치가 목표가 아니라 **CdBd 실제 옵션(각진/둥근/원형·가로/1:1·기본높이)으로 매핑**해 비교. Figma px를 그대로 통과시키면 에디터에 없는 값이 들어감(CLAUDE.md "모서리 3옵션·픽셀값 금지"). 리터럴 px 일치를 '정상' 판정하지 말 것. 오탐방지의 ±px 허용오차는 **legal 옵션 안에서의 오차**이지 비-legal 리터럴 인정이 아님.
- [ ] **D. 요청 목록 수정 후에도 V1~V5 전수 스윕 1회 필수** — 지적된 항목만 고치고 끝내면 목록 밖 이슈는 아무 스코프도 안 봄(5025 5건 공통 최대원인). 타깃 수정 후 전 카드×전 속성 스윕을 게이트로 통과 → 리로드 재검증.

## ⚠️ 영속화: block mutate로 되는 것 vs 패널 UI로만 되는 것 (2026-07-06 검증)
- **block mutate + reorder-commit으로 영속됨**: 텍스트 디자인(폰트·크기·색·정렬·줄간격 — `block.style` + `block.content` Lexical 둘 다)·줄바꿈(linebreak 노드)·모서리 `borderRadius`·배경 `background`·이미지 비율 `aspectRatio`·`multiCard.ratio`/`align`·`divider.*`·**`multiCard.items[].content`**(줄바꿈 linebreak + 줄별 inline 스타일 — 2026-07-07 5025 검증. 저장 시 paragraph `textStyle`/`textFormat`이 첫 run 스타일로 enrich되는 정규화는 리버트 아님)·프로필 `innerStyle.width`.
- **block mutate로 리버트(리로드 원복) → 패널/프리뷰 UI로만 영속**:
  - **카드 외부여백/내부여백**(특히 multiCard·reservation): `block.style.margin/padding` mutate는 리버트. **패널 "카드 디자인" 여백 컨트롤 = [슬라이더 | 텍스트필드 | 우측 아코디언 버튼(chevron)]. 아코디언 버튼 onClick → 상/하/좌/우 개별 필드가 펼쳐져 방향성 설정 가능**(2026-07-06 정정 — '단일값·structural 불가'는 오류였음). 각 방향 텍스트 필드에 키보드 입력 → `block.style`에 CSS shorthand로 커밋·영속(예: `margin:'0px 20px'`=좌우20 인셋, `padding:'4px 20px 8px'`=상4·좌우20·하8). multiCard·reservation은 "카드 디자인"이 MuiCollapse라 헤더 먼저 펼치고 field `scrollIntoView` 후 click. ⚠️ **필드 커밋 = blur 필요 (2026-07-07 5025 14카드 배치)**: 필드에 값 입력 후 `Enter`만 하고 **바로 다른 카드로 전환하면 그 값이 revert**됨(미커밋, in-session에서도 유실). → 값 입력 후 **다른 방향 필드(예: 상)를 click해 직전 필드를 blur→커밋**한 뒤 카드 전환. (첫 배치서 8/14 카드 bottom revert 원인 — top이 살아남은 건 다음 bottom 클릭 시 blur됐기 때문.) 셸은 zsh라 카드 루프는 **배열**(`CARDS=(...)`), 필드 식별은 y-범위보다 **방향 라벨(상/하/좌/우 @x≈1031)** 이 안정적.
  - **예약 콘텐츠**(버튼 텍스트·날짜·정원): 예약 정보 모달 + 프리뷰 contenteditable로만.
  - **위치 label/button/address**: 위치 카드 패널 토글 + 검색 지오코딩으로만.
- **패널 컨트롤 영속 방법**: **🥇 슬라이더 우측에 텍스트 필드(number input)가 있으면 슬라이더 대신 그 필드에 실제 키보드 입력**(`$B click 필드 → Meta+a → $B type "값" → Enter`) — 더 정확·안정(2026-07-06 사용자 지침). 텍스트 필드 없는 슬라이더·토글·칩만 **React fiber 외부 onChange 직접 호출**(페이지 색상 방식). 이미지 업로드는 dropzone `onDrop`. 예약/버튼 텍스트는 **프리뷰 contenteditable 실제 키보드**(`$B click #id → Meta+a → $B type`; `execCommand('insertText')`는 Lexical에서 무반응 ❌). 토글 연속 조작은 fiber 재쿼리(stale-closure 회피).

---

## ✅ 작업 원칙 (필수 준수) — 모든 스코프 공통

> 위 공통 지침 색상·라벨 원칙의 풀 체크리스트.

- [ ] **범용성** — 페이지뿐 아니라 **각 카드도 반복 복제**될 수 있게. 카드 1개 = 독립 의미 단위.
- [ ] **텍스트 카드 분리** — **하나의 텍스트 카드 = 하나의 텍스트 속성** *(⚠️ CdBd 제약이 아니라 **편집 용이성을 위한 우리 규칙** · 2026-09-07)*. 제목+본문을 한 카드에 묶지 말 것(편집 용이성).
- [ ] **보조 텍스트 색상** — 캡션·유의사항은 `{텍스트색} × N%`(투명도). 별도 회색 hex ❌.
- [ ] **테마 default 색상** — 색 쓰는 모든 요소는 `{버튼색}`/`{배경색}`/`{텍스트색}` 그대로. 카드별 커스텀 최소화.
- [ ] **장식 그래픽 배제** — 편집 불가 장식 이미지 ❌. 로고·프로필 등 교체 가능 이미지는 OK.
- [ ] **이미지 ≠ 텍스트** — 워드마크·문구를 이미지에 넣지 말 것(교체 시 편집 불가) → 이미지엔 **심볼만**, 워드마크·태그라인은 **텍스트 카드로 분리**.
- [ ] **카드 라벨 = 목적·내용 이름** — 기본 타입명("텍스트/이미지/구분선") 그대로 ❌ → 목적·내용 이름(예: 회사명·슬로건·여백·위치 안내). 카드 보드 가독성.

## 📐 디자인 통일성 (페이지 전역) — 모든 스코프 공통

> 페이지 단위 테마(색 1세트·서체 1개·버튼모양 1개)는 S1 「페이지 테마 체크리스트」 소관. 아래는 섹션 분리·모서리 톤 통일(여러 스코프 걸침).

- [ ] **섹션 분리 수단**: 구분선 카드(명확한 구분) · 여백 카드(구분선 두께 0/상하여백만 — 부드러운 구분) · 카드 배경색 그룹화 · 카드 모서리 둥글기.
- [ ] **카드 모서리 톤 통일** — 페이지 전체를 같은 톤(원형/각진/둥근)으로:
  - `{버튼모양}` 자동 적용: 메뉴 버튼·버튼·Q&A 제출·예약 버튼·위치 안내 버튼.
  - 개별 설정 필요: 이미지·갤러리·동영상·카드 자체 디자인 → `{버튼모양}`과 같은 톤으로 맞춤.

## 📐 텍스트 위계·런 스타일 — S3가 처음부터, V1/F1이 검증·수정

- **라벨+값 2속성 프레임 = 한 카드 2줄 + 런별 위계** — Figma 한 프레임에 작은 라벨 + 큰 값(예 `일시`/`2025.12.19`)이 있으면, 단일 텍스트 카드에 **2줄(라벨↵값)**로 채우되 **Lexical 런별로 다른 스타일**(라벨=작게·흐리게 12px·`{텍스트색}×70%` / 값=크게·진하게 18px·100%). 플레이스홀더로 남기거나 균일 스타일로 채우면 ❌. S3가 처음부터 처리(안 되면 F1/수동 런별 갱신).
- **텍스트 위계·색은 S3에서 Figma대로 처음부터** — fontSize·color·opacity·fontFamily(헤드라인 액센트 `{버튼색}`, 보조 `{텍스트색}×70%`, 섹션 제목 크게)를 카드별로 안 넣으면 V1이 diff를 20개+ 쏟아낸다(실측 21건). 처음부터 반영 = V/F 부하 대폭↓.
- **텍스트 색/크기 = `block.style` + Lexical `content` 런 style 양쪽** — 렌더 스타일은 `block.style`(fontSize·color·fontFamily) **그리고** `block.content` 각 런 `style` 문자열(`font-size`·`font-family`; color 없으면 block.style.color 렌더)에서 나온다. **런 style의 `font-size`가 block.style.fontSize를 오버라이드** → 크기 변경 시 반드시 둘 다 갱신. 런별 색은 런 style에 `color:` 주입.

## 🎨 카드 디테일 직접수정 4기법 (`blockById` + mutate → reorder 커밋)

1. **짧은 중앙 구분선**(섹션 타이틀 하단 액센트) = `block.style.padding`의 좌우값을 크게(예 `"20px 150px"` → 중앙 ~64px 라인).
2. **카드 외부 인셋**(Q&A·위치 등 섹션 카드를 가장자리서 띄움) = `block.style.margin="0px 20px"` (⚠️ 렌더 폭 측정 시 outer row는 full-width — 실제 인셋되는 건 배경 가진 자식 요소라 시각 확인이 정확).
3. **버튼 Outlined** = `block.innerStyle` `{background:"transparent", color:{버튼색}, borderColor:{버튼색}, borderWidth:"1.5px"}` (채움 = background={버튼색}·color={배경색}). ⚠️ **위치 안내 카드 내부 '지도 보기' 버튼은 Outlined 불가(채움 고정)**.
4. **한글 어절 중간 끊김 방지** = 문장 경계에 명시 개행(Lexical `content`에 `{type:"linebreak",version:1}` 삽입, 런 분할). `wordBreak:"break-all"` 전역 변경 ❌(에디터 미노출 = 비재현).

## 🚦 파이프라인 검증 게이트 함정

- **검증 에이전트 전멸(null) → `remaining=0` → `clean=true` 오판 = 거짓 클린** — `re.filter(Boolean).flatMap(r=>r.diffs)`식으로 짜면 V-에이전트가 limit·529로 전부 죽어도 diff 0 → clean으로 착각. **검증 성공 개수가 기대치(차원 수)에 못 미치면 clean 판정 보류 → 리포트에 「검증 미완」 표기.** 완료 보고 전 성공 검증 확인 필수.
- **weekly usage limit 도달 = 서브에이전트 전멸 + 메인 루프는 생존** — 이후 `agent()`는 실패하지만 메인 루프(직접 `$B`)는 동작 → 남은 수정은 `card-driver.js` 주입 후 `blockById` + 참조 mutate + `reorderCard` 커밋으로 직접 처리. 리셋 시각 확인 후 재개 판단.

## ⚠️ 공통 자동화 함정 (스코프 무관)

> 스코프 전용 함정은 각 S/F 에이전트 체크리스트 참조. 코드 레시피: skill `cdbd-card-automation`.

- [ ] **snapshot `@eN` ref는 매 호출 재번호** (함정14) — ref로 카드 식별 ❌ → **라벨 input value로 식별 → 부모 row 6단계 walk up → `elementFromPoint(r.left+50, r.top+r.height/2).click()`**.
- [ ] **`$B click`은 selector 전용** (함정9) — 좌표 클릭은 `document.elementFromPoint(x,y).click()` JS로.
- [ ] **`$B viewport`는 `1440x1024 --scale 1` 형식** (함정10) — `1440 1024`(공백 인자) ❌.
- [ ] **React form state는 native input setter로 안 들어감** (함정5) — 모달 input은 `$B fill`(keyboard 시뮬레이션 → form state 반영). native setter+dispatch만 쓰면 "값을 입력해주세요" 에러.
- [ ] **Reload 시 값 손실 = blur 미발생** (함정6) — input 변경 후 `blur` 강제 또는 `$B fill`(자동저장이 blur 트리거).
- [ ] **한글 attribute CSS selector 파싱 실패** (함정7) — Figma `node.query('[name*=시안]')` ❌ → `findAll(n => n.name.includes('시안'))` predicate.
- [ ] **모달 X 닫기 = absolute DIV**(button 아님·ESC ❌) (함정3) — `document.querySelector('div.absolute.right-\\[24px\\].top-\\[30px\\]').click()`.
- [ ] **"last contenteditable" focus = 페이지 최하단 카드** — y sort한 last로 입력하면 의도치 않은 카드(예: 버튼 텍스트)를 덮어쓴다 → **카드 보드에서 카드 명시 선택 후 우측 패널에서 입력**(mobile preview 의존 ❌).
- [ ] **카드 라벨 ✏️ pencil 우발 활성화 = 라벨 오염** — 보드 행 클릭 시 라벨 영역(span) 회피.
- [ ] **카드 추가 직후 mobile preview에 즉시 마운트 안 됨** — 추가 → 보드 명시 클릭 후 작업. **카드 보드 모달 열린 채 추출 ❌**(폼 필드 섞임 — 닫고 추출).
- [ ] **멀티페이지 에디터는 마지막에 본 페이지가 열림** — 열자마자 추출 ❌ → **명시적으로 페이지 1 클릭 후 추출**.
- [ ] 검증된 셀렉터·패턴·자동화 가능/수동 범위: skill `cdbd-card-automation`(Common mistakes·내부 동작).
