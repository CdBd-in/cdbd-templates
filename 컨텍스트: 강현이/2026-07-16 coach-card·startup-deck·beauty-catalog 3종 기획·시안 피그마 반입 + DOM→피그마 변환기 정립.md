---
created: 2026-07-16
updated: 2026-07-16
purpose: 신규 템플릿 3종(coach-card·startup-deck·beauty-catalog)의 1~3단계 진행 상황 + claude.ai/design 시안을 피그마 편집본으로 옮기는 방법론(DOM→피그마 변환기) 인수인계. 다른 디바이스에서 이어가기 위한 진입 문서.
---

# 세션 컨텍스트 — 2026-07-16 coach-card · startup-deck · beauty-catalog 3종 기획·시안 피그마 반입

> 공통 원칙·환경·계정·6단계 워크플로우는 [[../CLAUDE.md]] 참조 (여기 재기재 ❌)
> 이번 세션 = **신규 템플릿 3종을 1단계(기획) → 2단계(claude.ai/design 시안) → 3단계(피그마 편집본 반입)** 까지 진행.
> 가장 큰 산출물 = **claude.ai/design HTML → 피그마 편집 가능 카드 스택 변환기**([[#🛠 재사용 도구 (볼트 보존)]]).

---

## 🗺 현재 상태 한눈에

**Figma 파일**: `oi8zIHLfy59O5zV8aysqq4` (CdBd 템플릿 등록) · **페이지: 「사례 기획」 = `1:746`** (섹션이 전부 여기 있음. currentPage 기본값은 Cover라 스크립트마다 `setCurrentPageAsync` 필수)

| 템플릿 | 기획 문서 | 시안 HTML | 피그마 섹션 | 상태 |
|---|---|---|---|---|
| **coach-card** | [[3. 신규 템플릿 기획/coach-card — 기획]] | [[3. 신규 템플릿 기획/시안-coach-card.html]] | `1147:940` (x24388) | 3안 편집본 완료 |
| **startup-deck** | [[3. 신규 템플릿 기획/startup-deck — 기획]] · [[3. 신규 템플릿 기획/startup-deck — 기획 (멀티페이지)]] | [[3. 신규 템플릿 기획/시안-startup-deck.html]] | `1161:1026` (x26801) | **2a 확정** + 수정 반영 + 이미지 완료 |
| **beauty-catalog** | [[3. 신규 템플릿 기획/beauty-catalog — 기획]] | [[3. 신규 템플릿 기획/시안-beauty-catalog.html]] | `1255:23` (x29200) | 3안 편집본 완료(DOM 변환) · 이미지 미착수 |

### 주요 노드 ID
- **coach-card**: 1a=`1176:23` (자격 나열 → 2단 카드 변환·섹션 간격 48 적용) · 기타 1b/1c는 섹션 내
- **startup-deck 2a 확정본**: P1=`1181:23` · P2=`1182:23` · P3=`1183:23` · P4=`1184:23`
  - P1 히어로 이미지 자리 = `1176:326` (사용자가 만든 "Frame 44" 안의 rect)
  - **표지 시안 3종**: A(밝은 미니멀)=`1230:23` · B(다크)=`1230:59` · C(이미지 풀블리드)=`1230:95`
- **beauty-catalog**: 1a=`1293:23` · 1b=`1293:253` · 1c=`1293:140`

### 로컬 산출물
- `~/Desktop/coach-card/` · `~/Desktop/startup-deck/images/` (hero·heroA/B/C/E·heroP1/P2·prod1~4·team1~3)
- ⚠️ `/tmp/beauty-render`, `/tmp/startup-render`, `/tmp/coach-render` = **휘발성**. 재사용 도구는 볼트로 옮겨둠(아래).

---

## 🛠 재사용 도구 (볼트 보존) — 이 세션 최대 산출물

`1. 작업 가이드/도구/` 에 3개 저장. **다른 디바이스에서도 이것만 있으면 시안 반입 재현 가능.**

| 파일 | 역할 |
|---|---|
| `decode-claude-design.py` | claude.ai/design **standalone HTML → 실제 디자인 HTML** 추출 |
| `dom2fig.py` | 디자인 HTML → **DOM 트리 + flex/grid 레이아웃 계산**(폭·높이 산출) |
| `figma-dom-renderer.js` | 트리 → **피그마 오토레이아웃 노드**로 렌더(`buildPhone(D,X,Y)`) |

### 사용 흐름
```bash
python3 "1. 작업 가이드/도구/decode-claude-design.py" "~/Downloads/X (standalone).html" /tmp/sian.html
# → dom2fig.build(cardHTML, 390) 로 카드별 트리 생성 → JSON
# → figma-dom-renderer.js + `const D={theme,cards}` + `return await buildPhone(D,X,Y)` 를 use_figma 로 실행
```
- 빌드 파일이 20~30KB → `use_figma` code 한도(50KB) 내. **서브에이전트에 파일 읽어 실행시키면 메인 컨텍스트 절약**(이번에 계속 그렇게 함).
- `buildPhone(D,X,Y,{to:N})` / `{phoneId,from:N}` 으로 2패스 분할 가능(타임아웃 대비).

---

## 🔑 핵심 인사이트 (→ CLAUDE.md 승격 후보)

> 아직 CLAUDE.md에 반영 안 함. 다음 세션에서 승격 여부 판단 필요.

### 1. claude.ai/design 결과물 다루기
1. **standalone HTML = 번들러 껍데기**. 실제 디자인은 `<script type="__bundler/template">` 안에 **JSON escape된 문자열**(보통 파일에서 2번째로 긴 줄). `json.loads`로 디코딩.
2. **Export는 「Project HTML → standalone」** 선택 (PDF/PPT는 편집 불가).
3. 생성물은 **`<!-- 카드: 타입 -->` 주석**을 달아줌(생성 계약 덕분) → **카드 매니페스트를 그대로 추출 가능**. 단 `<!-- 페이지: -->` 주석은 멀티페이지판에만.
4. ⚠️ **마지막 변형(3안 중 3번째)은 뒤에 전체 복사본이 딸려옴** → 변형 분할 시 마지막 것만 꼬리 잘라내기 필요(coach 1c·startup 2c에서 발생).

### 2. 🚨 "카드 타입별 추정 빌더"는 실패한다 → DOM 변환기가 정답
이번 세션 최대 교훈. 처음엔 카드 타입(텍스트/갤러리/2단…)별로 추정해 그리는 빌더를 썼는데 **색·간격·폰트·구조가 계속 어긋나 4회 재작업**. 원인:
- **디자인이 전부 인라인 스타일 + `font:` 축약형**(`font:600 15px/1.3 'Pretendard'`) → `font-size`/`font-family` 키로 찾으면 **전부 None** → 크기·굵기·서체를 내가 추정하게 됨
- `padding:34px 30px 4px` 처럼 **간격도 실제 값이 있는데** 추정함
- `box-shadow:inset 0 0 0 1px …` = 테두리, `position:absolute` = 태그 오버레이, `aspect-ratio` = 이미지 비율 → 전부 추정 불가
→ **결론: HTML을 그대로 파싱해 옮겨라.** 추정 금지.

### 3. DOM→피그마 변환기 함정 (전부 실제로 밟음)
| 함정 | 해결 |
|---|---|
| **`<br>` 등 void 태그를 스택에 push** | 이후 형제가 br의 자식으로 중첩 → **음수 너비·요소 실종**. void 셋(`br,img,input,hr,image-slot`)은 push ❌ |
| `font:` 축약형 | `(\d+)\s+([\d.]+)px(?:/([\d.]+))?\s+(.+)` 로 weight/size/lh/family 분해 |
| **`aspect-ratio:1`** (슬래시 없음) | `'/' in ar` 체크만 하면 누락 → 이미지가 납작해짐. 숫자 단독도 처리 |
| **`display:grid`** 미지원 | 화보 2×2가 4줄로. → `HORIZONTAL + layoutWrap='WRAP'` + 자식 폭 `(inner-gap)/ncol` 고정 |
| `flex-wrap:wrap` 미지원 | 칩 내부 글자 깨짐 → `layoutWrap='WRAP'` |
| **`justify-content:center` 미매핑** | 버튼 라벨·아이콘이 왼쪽에 붙음 → `primaryAxisAlignItems='CENTER'` + 그 자식 텍스트는 FILL ❌(HUG해야 중앙에 옴) |
| **span(인라인)에 FILL** | 뱃지가 가로 전체로 늘어남 → span은 HUG |
| top-level `height:1px` | 구분선이 회색 덩어리 → 카드 최상위에도 height 적용 |
| 인라인 런(텍스트+span+텍스트) | 푸터가 3줄로 쪼개짐 → 한 텍스트로 합치고 `setRangeFontName/Size/Fills`로 런별 스타일 |

### 4. 피그마 API 함정 (신규)
1. **`upload_assets`에 nodeId를 줘도 fill이 자동 적용 안 됨**(`placedOnNodeId: null`). → **POST 응답의 `imageHash` 전체를 받아** `use_figma`에서 `node.fills=[{type:'IMAGE',imageHash,scaleMode:'FILL'}]` 직접 설정. nodeId 없이 업로드하면 임시 프레임이 생기니 해시 확보 후 삭제.
2. **텍스트 중앙정렬이 안 보이면 `layoutSizingHorizontal='FILL'` 누락**. 텍스트가 카드 폭을 안 채우면 `textAlignHorizontal=CENTER`가 무의미.
3. **기존 SECTION에 `appendChild` → 좌표가 섹션-상대로 바뀜**(CLAUDE.md 기존 함정과 동일하나 **createSection이 아닌 기존 섹션에도 적용됨**). 넣은 뒤 x/y를 섹션 기준으로 다시 설정할 것.
4. **`Cormorant Garamond`에 한글 글리프 없음** → 한글인데 serif면 텍스트가 안 보임. `hasKo(text)` 판정해 **`Noto Serif KR`** 폴백. (Figma에 Cormorant Garamond·Noto Serif KR·Gowun Batang 모두 있음)
5. `figma.currentPage`는 매 `use_figma` 호출마다 **첫 페이지로 리셋** → 작업 페이지 스크립트마다 `setCurrentPageAsync` 필수.

### 5. 이미지 생성 (gpt-image-1)
1. **AI가 만든 "가짜 UI 화면"은 히어로로 쓰면 티가 남** → 사용자가 3번 반려. **실사 사진** 또는 **제품을 실제로 보여주는 컷**이 답. 최종 채택 = "노트북에 Trigger→Condition→Action 워크플로우가 떠 있는 실사 제품 사진".
2. **히어로는 "그 제품이 뭔지" 보여줘야 함** — 차트 대시보드 사진은 워크플로우 자동화 제품과 안 맞았음(주제 적합성 > 화질).
3. bash 2분 타임아웃 → **8장 순차 생성은 초과**. `&` 병렬 백그라운드로.
4. 인물: `Realistic Korean facial features` + 역할별 복장 명시 → 품질 좋음(1회 통과).

---

## 📌 템플릿별 결정 흐름

### coach-card (피트니스 코치 영업용 명함 · 🔥 비비드)
1. 분류 = 프로필·명함 ② 상담·문의 유도 영업용 명함 / 페르소나 = 개인 PT·건강 코치
2. 3안(1a 풀블리드·1b 타이포·1c 갤러리) 피그마 편집본 반입
3. 수정: **자격 나열 메뉴 → 2단 카드**(연도 좌 FIXED + 내용 우 FILL) 4개 · **섹션 제목 위 여백 26→48**
4. 이후 사용자가 실제 이미지(코치 프로필·Before/After)·내용을 많이 채워 발전시킴

### startup-deck (투자자 IR 원페이저 · 💼 프로페셔널)
1. 분류 = 프로필·명함 ④ 브랜드 소개 홈페이지의 **IR 변형** / 예시 회사 = **리플로우(Reflow)**, 노코드 업무 자동화 SaaS
2. **원페이지판 + 멀티페이지판 기획 문서 2개** 작성 → 사용자는 **멀티페이지 3안(2a/2b/2c)** 생성
3. **2a(블루/화이트) 확정** — 이유: 가독성·범용성. (2c 골드 대시보드가 IR 본능은 좋으나 다크는 햇빛 취약)
4. 2a 복제 후 수정 4건: ①표지 상단 여백 ②2~4p **네비게이터(로고+홈 아이콘)** ③문제·솔루션=2b / 제품=2c로 교체(2a 톤 유지) ④표지로·다음 버튼 제거
5. 이미지 8장 생성·삽입 → 로고(Reflow 심볼+영문 워드마크)·네비 홈 아이콘은 **피그마 벡터**로 제작
6. **표지 3종**(A 밝은 미니멀·B 다크·C 풀블리드) 별도 제작 → **A에 위계 추가**(눈썹 `NO-CODE WORKFLOW AUTOMATION` · 제목 52px · 성과 한 줄 · `PRE-SEED IR DECK · 2026` 덱 라벨)
7. ⚠️ 사용자가 에디터에서 직접 편집 중 → 표지의 지표 대시보드 제거·이미지 자리(Frame 44) 생성 등 **내 작업과 사용자 편집이 교차**함. 작업 전 현재 상태 재확인 필수.

### beauty-catalog (클린뷰티 신제품 카탈로그 · 🌿 내추럴)
1. 분류 = 룩북·카탈로그 / **차별점 = Before/After 2단 카드**(기획서에 "모든 시안 필수"로 못박음 → 3안 전부 반영됨)
2. 예시 브랜드 = **ONDAM(온담)** · 3안(1a 화보 몰입·1b 카탈로그 나열·1c Before/After 중심)
3. **heuristic 빌더로 4회 실패 → DOM 변환기로 전면 재구축**해서 해결 (위 인사이트 2·3)
4. 정확값: 1a bg `#F5F1EA`/btn `#4F5A3F`(r16) · 1b bg `#F2F3EE`/btn `#37402F`(r12)·제품카드 흰색+inset 테두리 · 1c bg `#EFE7DB`/btn `#7A4A38`(r99 pill)
5. ⚠️ **1a에는 Q&A 폼이 원본에 없음** — `<!-- 카드: 질문과답변 (후기 대체 아님 — 후기는 텍스트) -->` 는 **메모 주석**(본문 비어있음). 옛 빌더가 없는 폼을 지어냈던 것. **빈 카드는 렌더에서 제외**해야 100px 공백이 안 생김.

---

## ⏭ 다음 세션 진입 우선순위

1. **beauty-catalog 3단계 마무리** — 시안 택1(또는 혼합) → **실제 이미지 생성**(화보컷·누끼컷·Before/After·무드컷). 현재 회색 자리표시 라벨("누끼컷" 등)이 박스 좌상단에 붙는 건 실제 이미지 넣으면 사라짐.
2. **startup-deck 표지 확정** — A/B/C 중 택1. A에만 위계 개선 적용됨(B/C는 미적용). **표지에서 다른 페이지로 가는 수단이 없음**(둘러보기·CTA 제거함) → ①작은 "시작하기 →" 버튼 ②서브 네비게이터로만 이동 중 택1 필요.
3. **coach-card 3단계 마무리** — 색·폰트 확정 + 나머지 이미지.
4. 3종 모두 → **4단계(CdBd 에디터 실제 제작)** 진입.
5. **인사이트 CLAUDE.md 승격 판단** — 위 「핵심 인사이트」 1~5. 특히 **"추정 빌더 ❌ → DOM 변환기"** 는 2단계→3단계 표준으로 굳힐 가치 있음. [[1. 작업 가이드/1-1. 워크플로우]] 3단계 절차에 도구 사용법 추가 검토.
6. ⚠️ **신규 `/draft` 스킬·D1~D5 에이전트**가 이번 세션 말미에 등장 — 프리셋 조합 기반 시안 제작(2단계 대체 후보). 이 세션의 "claude.ai/design → DOM 변환" 경로와 **관계 정리 필요**.

---

## 🧯 미해결 / 주의

- **사용자 편집과 교차**: startup-deck는 사용자가 Figma 에디터에서 직접 수정 중(Frame 44 생성, 지표 대시보드 삭제 등). 작업 전 `get_metadata`로 현재 구조 확인할 것.
- **beauty 자리표시 라벨 위치**: 원본 span에 centering이 없어 좌상단에 붙음(원본 충실). 실제 이미지로 교체되면 소멸 — 굳이 고치지 말 것.
- **`margin` 미지원**(변환기): `margin:0 6px` 같은 인셋이 무시돼 풀블리드로 렌더됨. 필요해지면 변환기 보강.
- **letter-spacing은 변환기가 의도적으로 버림** → CdBd 자간=0 규칙과 일치(정상 동작).
