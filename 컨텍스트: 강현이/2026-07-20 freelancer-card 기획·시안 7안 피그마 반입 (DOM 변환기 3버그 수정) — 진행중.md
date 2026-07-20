# 세션 컨텍스트 — 2026-07-20 freelancer-card 기획·시안 7안 피그마 반입 (진행 중·인수인계)

> 이전 세션: [[컨텍스트: 강현이/2026-07-16 coach-card·startup-deck·beauty-catalog 3종 기획·시안 피그마 반입 + DOM→피그마 변환기 정립]]
> 공통 원칙·환경·워크플로우는 [[../CLAUDE.md]] 참조. 이 문서는 **미완 작업 이어받기용**.
> 🛑 **중단 지점 = Figma MCP 연결 끊김(세션 한도, 19:50 KST 리셋). 남은 6안 렌더만 하면 끝.**

---

## 🎯 지금 무엇을 하던 중인가 (한 줄)

claude.ai/design이 만든 **freelancer-card 시안 7안**(HTML)을 **DOM→피그마 변환기**로 CdBd 편집 가능 카드 스택으로 옮기는 중. 변환기 **버그 3개**를 고쳤고, **5e 1안만 최종 반영 완료**, **나머지 6안(1a·2b·3c·4d·5f·5g) 재렌더가 남음**.

---

## ✅ 즉시 이어받기 — 재연결 후 이것만 하면 됨

### 1. Figma MCP 재연결 확인
- 증상: 대화 세션이 옛 연결 핸들을 붙듦 → `use_figma` 가 `MCP server "claude.ai Figma" is not connected`.
- `claude mcp list` 는 ✔ Connected로 나와도 **이미 떠 있는 대화 세션엔 반영 안 됨** → **`/mcp` 로 이 세션에서 재연결** 또는 **CLI 재시작** 필요.

### 2. 준비물 확인 (없으면 §"재생성 절차"로 복구)
- `/tmp/run4-{1a,2b,3c,4d,5f,5g}.js` — **테두리·폰트·italic 수정 전부 반영된 최종 렌더 스크립트** (각 ~43KB)
- ⚠️ `/tmp` 는 세션 넘어가면 사라질 수 있음 → 없으면 아래 재생성.

### 3. 남은 6안 렌더 (서브에이전트로, 파일 그대로 실행)
각 스크립트를 **general-purpose 서브에이전트**가 Read→`use_figma` code에 **그대로** 넣어 실행. (코드 요약·수정 금지) 좌표는 스크립트에 이미 박혀 있음:
| vid | x | 스크립트 |
|---|---|---|
| 1a | 33400 | `/tmp/run4-1a.js` |
| 2b | 33880 | `/tmp/run4-2b.js` |
| 3c | 34360 | `/tmp/run4-3c.js` |
| 4d | 34840 | `/tmp/run4-4d.js` |
| 5f | 35800 | `/tmp/run4-5f.js` |
| 5g | 36280 | `/tmp/run4-5g.js` |
(5e = x35320, **이미 반영 완료 · 노드 `1350:23`** — 다시 만들지 말 것)

### 4. 렌더 후: 섹션에 넣고 정렬 + 제목·테두리 검증
- 섹션 = **`1342:567`** ("freelancer-card", `사례 기획` 페이지 `1:746`)
- 각 폰 `sec.appendChild` 후 좌표를 **섹션-상대**로 재설정: `n.x = 절대x - sec.x; n.y = 3800 - sec.y`
- ⚠️ **기존 SECTION에 appendChild 하면 좌표가 섹션-상대로 바뀜**(변환기 정립 세션 함정 4-3).
- 검증: 각 폰 `findAllWithCriteria({types:["FRAME"]})` 로 `strokes.length>0` 개수 세서 §"검증 기준표"와 대조.

### 5. 완료 보고 = 섹션 스크린샷 + 노드 링크
`https://www.figma.com/design/oi8zIHLfy59O5zV8aysqq4/...?node-id=1342-567`

---

## 🔧 이번 세션에 고친 DOM 변환기 버그 3개 (→ 영구 도구에 반영 완료)

> 도구 위치: `1. 작업 가이드/도구/` — **버그 수정은 vault 파일에 이미 저장됨**(git status로 확인). `/tmp` 아님.

| # | 버그 | 원인 | 수정 파일 |
|---|---|---|---|
| **1** | **명조가 전부 Pretendard로 뭉개짐** | `expand()`가 `font:` 축약형 패밀리를 `serif/sans` 2값으로만 저장 → Cormorant 외 전부 sans. 나눔명조 344곳 증발 | `dom2fig.py`(패밀리 원문 보존) + `figma-dom-renderer.js`(`famOf()` 매핑 신설) |
| **2** | **`italic` 붙은 텍스트 = 크기·폰트 통째 증발** | `font: italic 400 26px ...` 처럼 style 키워드가 weight 앞에 오면 정규식 매치 실패 → 기본값 렌더 | `dom2fig.py` 정규식에 `(?:(?:italic\|oblique\|small-caps\|normal)\s+)*` 프리픽스 허용 |
| **3** | **구분선 전부 누락** | 렌더러가 `box-shadow:inset`만 테두리로 인식. 이 파일은 `border/border-top`(157곳)으로 그림 → 0개 반영 | `figma-dom-renderer.js` `applyBorders()`·`parseBorder()` 신설(변별 두께 `strokeTopWeight` 등) + `hasBox`에 `hasBorder` 추가 |

### 폰트 매핑 규칙 (famOf)
- **나눔명조·Batang·serif 계열 + 한글** → `Noto Serif KR`(본명조). 나눔명조는 **Figma에 없음**([[../1. 작업 가이드/1-4. 폰트]] 47행) → **CdBd 에디터엔 있으므로 4단계에서 원복**.
- Cormorant·Garamond·Instrument 등 **라틴 전용 세리프 + 라틴 글자** → `Cormorant Garamond`.
- 나머지 → `Pretendard`.
- **italic은 정체(Roman)로**(CdBd에 기울임 없음, CLAUDE.md 폰트 원칙 11).

### margin 지원도 추가
- 카드 **내부** margin은 투명 스페이서 프레임으로 재현(padding으로 접으면 `height:1px` 구분선이 두꺼워짐). 카드 **최상위는 margin 0** → 카드 간 간격은 원래부터 정상.

---

## 📋 검증 기준표 (재렌더 후 대조용)

원본 대비 **7안 전부 이미 검증 통과**한 수치 (D트리 빌드 시점):

| vid | 카드 | 세리프(원본=현재) | border(원본=D트리) |
|---|---|---|---|
| 1a | 26 | 0 = 0 | 18 = 18 |
| 2b | 18 | 1 = 1 | 25 = 25 |
| 3c | 22 | 6 = 6 | 27 = 27 |
| 4d | 22 | 0 = 0 | 22 = 22 |
| 5e | 23 | 19 = 19 | 18 = 18 (렌더 후 stroke 17개 확인됨) |
| 5f | 18 | 24 = 24 | 25 = 25 |
| 5g | 22 | 24 = 24 | 22 = 22 |

- 간격: 5e 23카드 최상위 padding **23/23 원본 일치** 확인됨(margin 0).
- ⚠️ **3c의 `Instrument Serif`**: 라틴 전용이라 한글 섞인 2곳=본명조 / 숫자·영문 4곳=Cormorant로 갈림. **원본 의도(단일 세리프)와 다름** → 3c 채택 시 한쪽 통일 필요(사용자 안내 완료).

---

## 🔄 재생성 절차 (`/tmp` 날아갔을 때 전체 복구)

원본 standalone: `/Users/mustard/Downloads/Freelancer Card (standalone) (1).html` (28MB, 존재 확인됨)

```bash
cd "/Users/mustard/Documents/GitHub/design/cdbd-templates"
# 1) 번들 껍데기 → 디자인 HTML
python3 "1. 작업 가이드/도구/decode-claude-design.py" \
  "/Users/mustard/Downloads/Freelancer Card (standalone) (1).html" /tmp/freelancer.html
# 2) 7안 분리 → /tmp/variant-{vid}.html
python3 "1. 작업 가이드/도구/split_variants.py"        # freelancer.html 경로 하드코딩
# 3) 변환기로 D-{vid}.json 생성 (테마 bg = class="scr" 배경, 껍데기 #fff 아님)
python3 "1. 작업 가이드/도구/build_D.py"
```
그다음 렌더 스크립트 조립(head에 페이지 전환 2줄 필수):
```python
r=open('1. 작업 가이드/도구/figma-dom-renderer.js',encoding='utf-8').read()
head='const __p = await figma.getNodeByIdAsync("1:746");\nawait figma.setCurrentPageAsync(__p);\n'
pos={'1a':33400,'2b':33880,'3c':34360,'4d':34840,'5f':35800,'5g':36280}  # 5e 제외(이미 완료)
for vid,x in pos.items():
    d=open(f'/tmp/D-{vid}.json',encoding='utf-8').read()
    open(f'/tmp/run4-{vid}.js','w').write(head+r+f'\nconst D={d};\nreturn await buildPhone(D, {x}, 3800);')
```
- ⚠️ `figma.currentPage` 는 매 `use_figma` 호출마다 첫 페이지로 리셋 → head 2줄로 `1:746`(사례 기획) 전환 필수.
- ⚠️ 변환기 `use_figma` code 한도(50KB) 내(~43KB). **서브에이전트에 파일 Read→실행 위임**해 메인 컨텍스트 절약.

---

## 🗂 노드 ID 지도 (현재 Figma 상태)

- 파일 `oi8zIHLfy59O5zV8aysqq4` · 페이지 **`1:746` (사례 기획)**
- 섹션 **`1342:567`** ("freelancer-card"), 제목 텍스트 `1342:568`
- **5e 완료본 = `1350:23`** (테두리·폰트 최종). 나머지 6안은 재렌더 직전 **삭제된 상태** → 섹션엔 지금 5e만 있음.
- 🗑 렌더 중 버려진 옛 노드ID들(1340~1349대)은 무시 — 이미 삭제됨.

---

## 🔗 관련 산출물

- **기획 문서**: [[../3. 신규 템플릿 기획/freelancer-card — 기획]] — 무드 **🎨 빈티지/노스탤직**(모던시크에서 변경). 프로필·명함 ②영업용 명함. 페르소나=1인 브랜드 디자이너 김도윤. 핵심 = **서비스 메뉴+가격 + 예산·일정 사전필터 Q&A**.
- **원본 7안**: 1a~4d(이전 라운드) + **5e·5f·5g(빈티지 무드 재생성본)**. 빈티지로 가기로 했으니 **5e·5f·5g 중 채택** 권장.
- **이미지**: 전부 회색 자리표시자 — 시안 확정 후 3단계에서 생성.
- **꼬리 잔여물**: 각 폰 맨 아래 얇은 가로선 = 휴대폰 홈 인디케이터 잔여(원본 껍데기). 확정본에서만 제거.

---

## 다음 세션 진입 우선순위

1. **Figma MCP 재연결**(`/mcp`) → §"즉시 이어받기" 3~5로 **남은 6안 렌더·정렬·검증**.
2. 사용자에게 **7안 스크린샷 제시 → 채택안 선택**(빈티지 5e/5f/5g 우선).
3. 채택 후: 좋은 부분 혼합 → **확정 시안** → 이미지 생성(gpt-image-1) → 4단계(CdBd 에디터).
4. (선택) **DOM 변환기 버그3 수정을 [[../CLAUDE.md]] 또는 도구 README에 승격** — 폰트 매핑·italic·border는 앞으로 모든 시안 반입에서 재발 방지 가치 있음. `split_variants.py`·`build_D.py`도 이번에 vault(`1. 작업 가이드/도구/`)로 영구 보존함.

---

## 세션 종료 점검
- [x] 영구 룰(변환기 버그3 수정) = **도구 파일에 반영 완료**(dom2fig.py·figma-dom-renderer.js) · 중간 스크립트 2개 vault 보존
- [x] CLAUDE.md 중복 없음 (환경·워크플로우 재기재 안 함, 링크만)
- [x] 미완 작업 = "남은 6안 렌더"로 최상단 명시
- [ ] 변환기 버그3의 CLAUDE.md 승격 = **다음 세션 판단**(우선순위 4)
