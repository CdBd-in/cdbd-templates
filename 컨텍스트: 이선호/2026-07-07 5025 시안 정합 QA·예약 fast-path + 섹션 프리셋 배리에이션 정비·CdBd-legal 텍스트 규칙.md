---
created: 2026-07-07
merged_from:
  - "2026-07-07 5025 시안 정합 QA·예약 fast-path·에이전트 갱신"
  - "2026-07-07 섹션 프리셋 배리에이션 정비 — 3페이지 원본+3배리·CdBd-legal 텍스트 규칙"
purpose: "같은 날(2026-07-07) 두 스레드를 합친 핸드오프. ① 5025 시안 정합 QA·예약 dayjs fast-path·에이전트 갱신 ② 섹션 프리셋 3페이지 원본+3배리 정비 + CdBd-legal 텍스트 규칙 3종."
---

# 세션 컨텍스트 — 2026-07-07 (두 스레드 합본)

> 같은 날 진행된 **두 개의 스레드**를 하나로 합친 문서. 공통 원칙·환경은 [[../CLAUDE.md]] 참조.
> - **스레드 1** — 5025 시안 정합 QA·예약 fast-path·에이전트 갱신 (아래)
> - **스레드 2** — 섹션 프리셋 배리에이션 정비·CdBd-legal 텍스트 규칙
> 이전 세션: [[컨텍스트: 이선호/2026-07-06 에디터 파이프라인 설계·검증 + 워크플로우 개편(Claude Design·개방형 명세)]]

---

## 세션 컨텍스트 — 2026-07-07 5025 시안 정합 QA·예약 fast-path·에이전트 갱신

> 이 문서는 새 대화에서 작업을 바로 이어갈 수 있도록 작성된 컨텍스트 파일이다.
> 이전 세션: [[컨텍스트: 이선호/2026-07-06 에디터 파이프라인 설계·검증 + 워크플로우 개편(Claude Design·개방형 명세)]]
> 공통 원칙·환경·워크플로우·카드 정책은 [[../CLAUDE.md]] 참조(재기재 ❌). **영구 룰은 각 에이전트/스킬/shared에 이미 기록** — 여기엔 흐름·상태·정정 사이클·재사용 스크립트만.

---

### 작업 파일

- **대상 에디터:** `https://www.cdbd.in/editor/5025` (교회 40주년 초대장, 17카드) — 파이프라인 검증/QA용 테스트 에디터
- **기준 Figma:** `oi8zIHLfy59O5zV8aysqq4` / node `964-1600` (`church-rsvp` 섹션 = Claude Design B+C, 380×1664) — **CdBd 템플릿 등록 파일 안**
- **수정 문서 (에이전트 체크리스트/방법):**
  - `.claude/agents/cdbd-edit-s3-text.md` *(복합정보 줄바꿈 / 줄별 스타일 다름→F1)*
  - `.claude/agents/cdbd-edit-s4-image.md` *(3x export / 채워진 카드 교체 / 사전 업로드→applyImage)*
  - `.claude/agents/cdbd-edit-v1-textdesign.md` *(런별 부분 디자인)*
  - `.claude/agents/cdbd-edit-v2-imageshape.md` *(프로필 innerStyle.width)*
  - `.claude/agents/cdbd-edit-v5-carddesign.md` *(내부/외부 중복·최하단≥40·per-card 패딩 시안 대조)*
  - `.claude/agents/cdbd-edit-f1-fix.md` *(신규 ✅ 체크리스트)*
  - `.claude/agents/cdbd-edit-s6-reservation.md` *(날짜·시간 fast-path 포인터)*
  - `.claude/cdbd-edit-shared.md` *(영속화 표 3건 추가)*
  - `.claude/skills/cdbd-card-automation/SKILL.md` *(예약 dayjs onChange fast-path)*
  - `docs/superpowers/plans/2026-07-06-cdbd-editor-pipeline.md` + 이전 컨텍스트 *(stale Figma ref 정정)*
- **참조:** [[1-6-1. CdBd 에디터]] · [[1-6-2. CdBd 카드 기능]] · skill `cdbd-card-automation`

---

### 오늘 완료한 작업 (2026-07-07)

#### A. 5025 ↔ 시안(964-1600) 정합 — 사용자 요청 수정 (1라운드 5건)

| # | 수정 | 담당 | 결과 |
|---|---|---|---|
| 1 | 로고·예배당·목사 이미지 시안과 상이 | **S4** | 964-1600에서 3배수 rawImage 추출→교체(로고=투명 골드 심볼 1045²·예배당 1024²·목사 1024²). 리로드 영속 |
| 2 | 카드 상하 여백 내부/외부 중복 확인 | (inline) | "중복 없음=clean" 판정 → **오판**(→ D에서 정정) |
| 3 | 세션 일시 줄바꿈+색/웨이트/사이즈 | **F1** | multiCard 5·7·9의 4개 item 원자 재작성 |
| 4 | 프로필 이미지 확대 | **F1** | `innerStyle.width` 15%→**17%** (×1.15) |
| 5 | 마지막 카드 하단 여백 ≥40 | **F1** | 20→40 (→ D에서 시안값 **44**로 갱신) |

#### B. 추가 요청 (2라운드)

- **예배당 이미지 모양 확인** → 시안 일치(`aspectRatio 1/1`+`borderRadius 14px`+object-cover), 수정 불필요.
- **S2 카드명 17개** → 목적 라벨(로고/헤드라인/인사말/예배당 사진/전체 회차 안내/회차 요약/신청 안내/1·2회차 제목·일시/1·2회차 참석 신청/구분선/담임목사/위치 제목/예배당 주소/위치 안내/운영팀 연락). 수렴 루프 16회 set, 영속.
- **여백 재정정(#2 오해)** → 아래 D.

#### C. Figma stale ref 정정

지난 세션 기록의 `2CX6W3Zg9OzbBiwIZ9Tk6J`/`8-3425`는 **그 파일이 다른 시안(AI 워크플로·타 템플릿 목업)으로 교체돼 node 삭제**됨. 교회 시안은 `oi8zIHLfy59O5zV8aysqq4`/`964-1600`으로 이동. plan 문서·이전 컨텍스트의 T16 참조·기준 Figma 정의를 정정.

#### D. 여백 정정 — 14카드 상하 패딩 시안값으로 (핵심)

사용자 clarify: "상하여백 확인"의 의도는 **중복 여부**가 아니라 **시안 대비 과다** 여부. CdBd 기본 20/20 균일이 시안보다 넓음.

| 카드 예시 | 전(상/하) | 후(상/하, 시안) |
|---|---|---|
| 로고 | 20/20 | **30/14** |
| 헤드라인 | 20/20 | **2/10** |
| 담임목사 | 20/20 | **2/28** |
| 운영팀 연락(마지막) | 20/40 | **6/44** |

- page gap=0 → **카드A 하단 padding + 카드B 상단 padding = 실제 간격**. 로고↔타이틀: CdBd 40 → 시안 **16**.
- 14카드 변경(예약 2·구분선 1은 이미 근접/일치라 제외). F1 패널 여백 아코디언, 리로드 영속.

#### E. S6 예약 시간 단축 — dayjs onChange fast-path (신규 능력, 검증)

구 2026-06-24 "dayjs onChange 불가" 판정을 **뒤집음**. 5025 예약 모달에서 라이브 검증(저장 안 함, 데이터 무손상).

| | 기존(픽커 클릭) | fast-path |
|---|---|---|
| 옵션당 날짜·시간 | ~2초 | onChange 2회 ~0.2초 |
| 옵션당 총 | ~5초 | **~2초** |
| S6 전체 | — | **~50-60%↓** |

- 요일 `(토)`까지 자동 파생(기존 "타이핑" 방식이 못 풀던 문제). → skill에 레시피 기록.
- **더 큰 천장(미착수):** 예약 저장 네트워크 요청 재현(API-direct) → 모달 전체 스킵(45초→~1초). 단 auth·payload 리버스 + DB 직접 쓰기 리스크 → 대량 예약 세팅 필요 시 검토.

#### F. S4 워크플로 변경 (사용자 결정)

이미지 업로드는 **앞으로 사용자가 미리 라이브러리에 올림** → S4는 업로드 생략, `applyImage`만. (S4 최대 병목이 업로드였음 — 이번 세션 실측 17분/3장.)

---

### 정정 사이클 (왜 — 다음 세션 참고)

1. **#2 여백**: "padding+margin 중복 없음 = clean"(오판) → 사용자 "시안 대비 넓다, 페이지 전반 반복" → **각 카드 상하 패딩을 시안 프레임값과 대조**가 정답. V5 체크리스트에 반영.
2. **세션 일시 라우팅**: 줄바꿈(S3)+색/웨이트/사이즈(V1→F1)로 나누려다, **줄마다 스타일이 달라** 단순 linebreak 불가 → **F1이 content를 줄별 text 노드+inline 스타일로 원자 재작성**(S3·V1 통합). S3/F1 체크리스트에 경계 명시.
3. **여백 batch revert**: F1 첫 배치서 8/14 카드 bottom이 되돌아감 → **필드 입력 후 blur(다른 방향 필드 click) 해야 커밋**, Enter만+카드전환은 revert. shared.md·F1 체크리스트 반영.
4. **Figma ref**: 8-3425(stale) → 실사용 964-1600. 파일 내용으로 교회 문자열 0건 확인 후 사용자에게 위치 재요청.

---

### 재사용 스크립트 (검증됨)

**예약 날짜·시간 = dayjs onChange 주입** (skill 풀버전: `cdbd-card-automation#날짜·시간 픽커`)
```js
// 1) 어댑터 추출(모달당 1회) — 날짜 input fiber의 context에서 .date() 보유 객체
var di=[...document.querySelectorAll('input')].find(e=>e.placeholder==='날짜를 선택해 주세요');
var f=window.__cdbd.fiberOf(di),adapter=null,d=0;
while(f&&d<25){var dep=f.dependencies&&f.dependencies.firstContext;while(dep){var v=dep.memoizedValue;if(v){var c=v.utils||v;if(typeof c.date==='function')adapter=c;}dep=dep.next;}if(adapter)break;f=f.return;d++;}
// 2) 주입 — onChange 식별은 소스 isValid()(depth 아님; depth~13은 MUI 내부라 무효)
function inject(ph,iso){var i=[...document.querySelectorAll('input')].find(e=>e.placeholder===ph);var f=window.__cdbd.fiberOf(i),fn=null,g=0;while(f&&g<25){var p=f.memoizedProps;if(p&&typeof p.onChange==='function'&&/isValid\(\)/.test(p.onChange.toString())){fn=p.onChange;break;}f=f.return;g++;}return fn(adapter.date(iso));}
inject('날짜를 선택해 주세요','2026-10-17T00:00:00'); // → "2026.10.17(토)"
inject('시간을 선택해 주세요','2026-10-17T19:30:00'); // → "19:30"
```
**예약 모달 취소(저장 폐기)**: X셀렉터(`div.absolute.right-[24px]…`)는 예약 모달에 없음 → **푸터 "취소하기"(="변경사항 저장하기" 형제) click → "나가기"**.

**시안 per-card 패딩 산출**: `get_metadata`의 프레임 h + 내부 자식 y/h → top=child.y, bottom=frame.h−child.y−child.h. (실측 3건과 일치: 예배당 pt2/pb20, overview pt2/pb14, 세션 pt8/pb12 — `get_design_context`의 `pt-`/`pb-`로 교차검증.)

---

### 5025 최종 상태 (964-1600 정합)

- 이미지 3개 교체(로고 투명 심볼·예배당 본당·목사 인물) · 세션 일시 4항목 줄바꿈+줄별 디자인(제목 Batang Bold 17/#020826, 일시 Dodum 13/rgba .65; 오버뷰 시간 18px) · 프로필 17% · **14카드 상하 여백 시안값** · 카드명 17개 목적 라벨.
- 예약 카드(idx8·10)·위치·Q&A 등 **콘텐츠는 미변경**(정합 범위 밖).

---

### 미완료 / 향후 확인 필요

- [ ] **S6 fast-path 옵션당 실측** — 다음 예약 카드 실제 세팅 시 시간 찍어 skill에 반영
- [ ] **API-direct 예약 저장 재현** — 대량 예약(수십 개) 필요 시 검토(auth·payload 리버스)
- [ ] 5025 예약 2건(idx8·10) 실제 날짜·시간·정원·방문체크 세팅은 아직 안 함(테스트 에디터라 보류)
- [ ] (기존) 소식·매거진 카테고리 첫 템플릿 · 상품 카드 활용 템플릿 · 분석용 에디터 4827~4843 정리

---

### 핵심 설계 결정사항

- **줄별 스타일 다른 텍스트 = F1 원자 재작성**: 줄마다 색/웨이트/사이즈가 다르면 S3 linebreak+V1 diff로 분리 불가 → content를 줄별 text 노드+inline 스타일로 한 번에. (`multiCard.items[].content`도 mutate+reorder-commit 영속 검증.)
- **카드 여백 = 패널 전용 + blur 커밋**: `block.style.padding` mutate는 리버트(재확인) → 아코디언 필드 키보드 입력 + **다른 필드 click으로 blur 커밋** 후 카드 전환.
- **여백 판정 기준**: "중복 없음"이 아니라 **시안 프레임값 대조**(CdBd 기본 20 균일이 대체로 넓음).

---

### 피그마 파일 정보

| 항목 | 값 |
|------|----|
| 파일 키 | `oi8zIHLfy59O5zV8aysqq4` (CdBd 템플릿 등록) |
| 교회 시안 노드 | `964-1600` (`church-rsvp` 섹션, 380×1664, 17프레임) |
| 주요 하위 노드 | 로고 `964:1603` · 예배당 `964:1608/1609` · 목사 `964:1647` · 세션 오버뷰 `964:1612` · 세션 헤더 `964:1625` |
| ⚠️ stale(삭제) | 구 `2CX6W3Zg9OzbBiwIZ9Tk6J`/`8-3425` — 사용 금지 |

---

## 세션 컨텍스트 — 2026-07-07 섹션 프리셋 배리에이션 정비 (밀과버터·교회·채용)

> 이전 스레드(같은 날 · 본 문서 위): 5025 시안 정합 QA·예약 fast-path·에이전트 갱신
> 작업 베이스: [[1. 작업 가이드/1-8. 섹션 프리셋 라이브러리]] · 공통 원칙·환경은 [[CLAUDE.md]] 참조
> 주제: Figma "섹션 프리셋" 3페이지(밀과버터 `966:3731` / 교회 `966:3014` / 채용 `966:3732`)를 **원본+3배리(4열 그리드)**로 정비 + **CdBd-legal 텍스트 규칙 3종** 신규 정립. 파일키 `oi8zIHLfy59O5zV8aysqq4`.

---

### 1부 — 신규 영구 규칙 (→ 정본에 기록, 여기선 링크만)

**[[CLAUDE.md]] 기록:**
1. 줄간격 = **짝수 소수 우선**(1.2·1.4·1.6), 1의 자리 세분화 ❌ → 폰트 원칙 #10
2. **버튼 default = 원형(pill)** → 카드 기본 기능·디자인 섹션
3. **내부 간격 고정 카드**(Q&A·프로필·위치) = 실제 에디터 값만, 배리는 카드 디자인으로 → 🧩⑥
4. **이탤릭체 금지**(CdBd 옵션 없음) → 폰트 원칙 #11
- (앞 세션 기록) 지도 모양·비율 = **각진/둥근 × 가로/1:1만** → 🧩⑤

**[[1. 작업 가이드/1-8. 섹션 프리셋 라이브러리]] 보강:**
- 기준 2: **배리 개수 = 원본+3** / **차별화 깊이**(카드 순서만 ❌ → 정렬·배경·구분선) / **반복 하위섹션 = "구분 방식"을 변주 축으로**
- **기능 고정 카드 = 내부 고정·카드 디자인은 배리 가능**(개정 — 기존 "변형 대상 ❌"에서 완화)
- 카탈로그 3)·4)·5) = 밀과버터·교회·채용 프리셋 세트(섹션별 A/B/C/D 표 + Figma 링크)

---

### 2부 — 정정 사이클 (역사적 로그)

#### 라운드 1 — 사용자 피드백 5건 (주로 밀과버터)
1. **"배리에이션 = 원본 제외 3개"** → 기존 원본+2였음을 원본+3으로(각 섹션 **D 열 추가**).
2. **"About/Classes가 카드 순서만 다르고 강약·레이아웃 동일"** → 정렬(좌/중)·배경(투명/틴트카드)·구분선(액센트바/풀divider)·이미지 위치로 **실질 차별화**.
3. **"Classes에 반복 2섹션(입문반+심화반) 포함"** — 원본이 두 반을 담아 "섹션 구분법"을 보여주려던 것 → B/C/D 모두 **두 반 포함** + 구분 방식(구분선/틴트카드/번호01·02) 변주.
4. **"Contact(동등 2버튼) 배리 필요"** → 세로 스택 / 라벨+2단 틴트카드 / 아이콘 리스트.
5. **"Form = 에디터 가능 배리(여백·배경·간격)"** → Q&A 내부는 **동일 복제**(기능 고정), 카드 **배경·모서리·테두리만** 변주 + 제목 중앙.

#### 라운드 2 — 이탤릭 금지
- CdBd 에디터 이탤릭 옵션 없음 → 규칙화 + **5섹션(밀과버터·교회·채용·gala 964:1314·ROOFTOP 964:2485) 506개 텍스트 스캔 = 이탤릭 0건**(mixed 세그먼트 포함). 수정 없음.

#### 처리 결정
- **기능 고정 섹션(위치·Q&A·Reservation)도 원본+3로** — 단 내부 고정, **카드 디자인만** 변주.
- **교회 claude.ai import 스캐폴딩 3프레임 제거**(`1011:4994/5058/5122`) → 밀과버터처럼 클린 A/B/C/D 그리드.
- **Location A 정합 수정**: 아웃라인 버튼 → 채움 pill, 빈 흰 지도 → 회색 플레이스홀더+📍라벨(각진 가로), 주소 중앙.

#### 결과 (섹션 트림 후)
| 페이지 | 노드 | 크기 | 변주 섹션(각 A/B/C/D) |
|---|---|---|---|
| 밀과버터 | `966:3731` | 2000×3153 | 프로필·About·Classes·Contact |
| 교회 | `966:3014` | 2000×2306 | 히어로·Sessions·위치+연락 |
| 채용 | `966:3732` | 2000×2840 | 히어로·Date&Location·Form·Reservation |
- 줄간격 정규화 합계 **54개**(150%·AUTO → 짝수), 버튼 원형화 **11개**(교회 6+채용 5), 자간 0·이탤릭 0.

---

### 3부 — 재사용 스크립트·함정

#### use_figma 헬퍼 패턴 (프리셋 빌드)
- **`vcard(name,x,y,{bg,pad,gap,radius,border})`** — VERTICAL auto-layout. `resize()` 후 **`primaryAxisSizingMode='AUTO'` 재설정**(리사이즈가 FIXED로 리셋하는 알려진 함정).
- **`mk(chars,style,size,color,op,align,lhv)`** — `letterSpacing:{PERCENT,0}` 필수, `lineHeight` 짝수 PERCENT 기본(Bold 140 / Regular 160).
- **`fullBtn`** — HORIZONTAL, `paddingTop/Bottom 15~16` + `counterAxisSizingMode:'AUTO'`로 높이 확보(resize 회피), `cornerRadius 99`(원형), 텍스트 `#fafafa`.
- **`mapBox(parent,ratio,radius)`** — 가로=`w/1.5`, 1:1=`w`. 회색 `TXT@0.06` + 📍 지도 라벨 중앙.
- 이미지 재사용: `fills=[{type:'IMAGE',imageHash:HASH,scaleMode:'FILL'}]` — 원본 프레임 fills에서 hash 회수해 주입.

#### 정규화 스윕 (섹션 단위, 재사용 가능)
- **줄간격**: `findAll('TEXT')` → PERCENT면 `Math.round(v/20)*20`(짝수 보장), AUTO면 Bold140/Reg160.
- **버튼 원형**: PT-fill(108,76,255 ±tol) 프레임 중 **`width>120 && height<90 && width/height>2.2`** 만 `cornerRadius=99` (로고 배지·컬러 밴드 제외 — 종횡비 가드 핵심).
- **이탤릭 스캔**: `fontName.style` `/italic/i`, mixed는 `getStyledTextSegments(['fontName'])`.
- **섹션 트림**: children 최대 우/하 + 80 여백 `resizeWithoutConstraints`.

#### 함정
- **Edit 툴이 한글·중점(·) 포함 라인 앵커에서 "string not found"** — 문자 정규화 이슈로 긴 앵커 매칭 실패. → **Python splice(`open`→`find`→`write`)로 우회**(byte 매칭 정확, guard로 이중삽입 방지). 1-8 카탈로그 삽입에 사용.
- 섹션 자식 좌표 = **섹션-상대**. 4열 컬럼 x=**100/580/1060/1540**, 폭 380.
- get_screenshot URL → `curl` 다운로드 후 Read로 시각 확인(멀티 배리 검증).

---

### 다음 세션 진입 우선순위
1. **(선택) gala `964:1314` · ROOFTOP `964:2485`에도 동일 정비** — 원본+3 확인 + 글로벌 규칙(줄간격 짝수·버튼 원형·이탤릭 0) 스윕. 현재 3페이지만 완료(gala/ROOFTOP는 이탤릭 0만 확인).
2. **검증된 5개 프리셋 세트 → 신규 템플릿 실제 조립**에 사용([[1. 작업 가이드/1-8. 섹션 프리셋 라이브러리]] 워크플로우 3단계 · 무드 색·폰트만 갈아끼움).
3. **소식·매거진 카테고리(0개) 첫 템플릿** — 미충족 분야 우선.
4. 프리셋 → **4단계 CdBd 에디터 전이 실사용 테스트**(평탄화·여백 정합 확인).
