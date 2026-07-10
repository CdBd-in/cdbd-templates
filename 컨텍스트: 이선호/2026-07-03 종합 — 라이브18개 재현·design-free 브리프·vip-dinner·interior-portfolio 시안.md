---
created: 2026-07-03
session_topic: "하루 4개 작업 스트림 통합 — (1) 라이브 18개 에디터 구조 피그마 재현 파이프라인 (초대·예약 6개 완성) (2) vip-dinner 시안 제작·template-brief design-free 전환·에디터 이전 시도 (3) interior-portfolio 멀티페이지 브리프 개정·claude design 시안 3종 피그마 이전 (4) interior-portfolio 여백-스케일 CdBd 시안 직접 제작·내추럴 무드 적용"
related: "[[../CLAUDE.md]], [[../3. 신규 템플릿 기획/3-0. 신규 템플릿 18건 정리]], [[../2. CdBd 템플릿 현황/.data/live-editor-structures/_index.md]], [[../.claude/skills/template-brief/SKILL.md]], [[../1. 작업 가이드/1-0. 템플릿 기획 워크플로우]], [[2026-06-19 웨딩 초대장 3시안 리팩토링·여백 우선순위 원칙 진화]]"
---

# 세션 컨텍스트 — 2026-07-03 (종합)

> 이전 세션: [[2026-06-19 웨딩 초대장 3시안 리팩토링·여백 우선순위 원칙 진화]]
> 같은 날짜의 4개 작업 스트림을 하나로 합침. 각 부는 독립 작업이나 날짜 동일 → 사용자 규칙 "오늘 날짜 세션 컨텍스트 하나로 병합".
> 공통 원칙·환경·계정·자동화 함정·워크플로우 풀버전: [[../CLAUDE.md]] 참조 (여기서 재기재 X).

**작업 스트림 요약**

| 부 | 주제 | 핵심 산출물 |
|---|---|---|
| 1부 | 라이브 18개 에디터 구조 피그마 재현 | page node `900-23` · 초대·예약 6개 프레임 · 추출→변환→빌드 파이프라인 |
| 2부 | vip-dinner 시안 + template-brief design-free + 에디터 이전 시도 | 피그마 `2CX6W3Zg9OzbBiwIZ9Tk6J` node `8-4333` · 스킬 단일 모드 통합 |
| 3부 | interior-portfolio 멀티페이지 브리프·claude design 3종 이전 | 시안 보드 `948:32` (3행 A/B/C × 4열) |
| 4부 | interior-portfolio 여백-스케일 CdBd 시안 직접 제작·내추럴 무드 | 시안 섹션 `947:23` (5페이지, 내추럴 무드 HappyHues 8) |

---

## 1부 — 라이브 18개 템플릿 에디터 구조 피그마 재현

> **신규 기획 아님** — https://www.cdbd.in/templates 의 기존 라이브 템플릿을 "템플릿 사용하기"로 에디터 진입 → 실제 구조 추출 → 피그마 재현. 각 프레임명 = **오리지널 카드 타입**(수정 라벨 X). 재현 수준 = **C-이미지**(실제 텍스트·색·폰트·패딩 재현, 이미지만 회색 플레이스홀더).
> **빌드 아키텍처·폰트맵·파이프라인 상세**: [[../2. CdBd 템플릿 현황/.data/live-editor-structures/_index.md]] (영구 기록).

### 1-0. 개요
| 구분 | 내용 |
|---|---|
| 작업 | 라이브 초대·예약 카테고리 7개 중 **6개** 에디터 구조 재현 |
| 피그마 | CdBd 템플릿 등록 파일 → **새 페이지 "기존 18개 · 에디터 구조"** (node-id `900-23`) |
| 완성 프레임 | seminar `934:23` · reservation `940:23` · rsvp `941:23` · personalized `938:23` · popup `942:23` · recruit `943:23` (전부 380폭, x=0/460/920/1380/1840/2300) |
| 확정 | 빌드 아키텍처 4대 요건 · 요소별 실제 폰트 매핑 9종 |

### 1-1. 결정 흐름 (다회 정정 4라운드)
1. **근사 재현 (반려)** — 렌더 텍스트+일부 computed만 샘플링. 반려 4사유: 폰트 부정확(전부 Pretendard)·색/버튼색 임의·Q&A 인풋(체크박스/입력창) 생략·여백 하드코딩. 교훈: "렌더 텍스트만 뽑기"는 구조 재현 아님.
2. **절대좌표 픽셀 재현** — 요소별 rect+computed CSS 그대로 추출·절대배치. 패딩·섹션배경(#eaedf0, Q&A #f2f2f5)·폼 인풋·제출 pill까지. 여전히 폰트 Pretendard 일괄 → 반려.
3. **요소별 실제 폰트 발견** — `getComputedStyle().fontFamily` 첫 토큰 뽑으니 템플릿마다 테마 폰트 상이: reservation=Bebas Neue+ChosunilboNM · rsvp=Cafe24 ClassicType · personalized=Playfair Display+GounBatang(→KoPub Batang 대체) · popup=Anton · recruit=Montserrat. → "Pretendard 일괄 금지, 요소별 computed font-family 추출·매핑" 확정.
4. **최종 아키텍처 (사용자 명시)** — 페이지 배경색 fill · 프레임 width=380 · 텍스트박스 FILL 폭 · 1 텍스트카드=1 텍스트박스 · 전 카드 오토레이아웃. 절대배치 버리고 오토레이아웃+텍스트 병합으로 전환, 6개 전부 적용.

### 1-2. 확정 빌드 아키텍처 (요건)
1. 프레임 width 380 (카드=FILL).
2. 페이지·카드 전부 오토레이아웃. 배경 있는 인셋 섹션 = **외부여백 wrapper + 내부 fill 프레임** 2-depth (CLAUDE.md Auto Layout 규칙 일치).
3. 1 텍스트카드=1 텍스트박스. 행별 스타일 `setRange*`, 세로 간격 = 각 행 line-height = (다음 행 y − 현재 행 y) 로 원본 리듬 재현.
4. 페이지 배경색=실제 테마값. 다크(popup #a23721, recruit #16161a)=카드 투명+흰 글씨, 라이트=흰 글씨 카드에 다크 fill(#1a1a1a) 폴백.
5. 폰트=요소별 실제 매핑. Figma 확보 서체: Pretendard/Bebas Neue/ChosunilboNM/Cafe24 ClassicType OTF/Playfair Display/KoPub Batang(=GounBatang 대체)/KoPubWorldDotum_Pro/Anton/Montserrat/Noto Serif KR.
6. 이미지·갤러리·프로필·지도=회색 `[타입]` 플레이스홀더. Q&A만 fixed 프레임 내 absolute 폼. 버튼/예약/CTA=pill.

### 1-3. 재사용 자산 (`.data/live-editor-structures/`)
- **추출 `extract_abs.js`**: 카드타입=카드보드 `rect[rx="4"]` SVG 첫 path `d` 40자 → `.data/card-type-mapping.json`. 콘텐츠=`.overflow-y-scroll > .flex.min-h-full.flex-col > .cursor-pointer` 카드별 rect+font/색/align/line-height+카드배경+box+input+img. 카드보드↔프리뷰 1:1 zip.
- **변환 `transform3.py`**: 타입별 모델(`nb_*.json`) — 텍스트=tp, 이미지=imgs, 위치=map+addr+cta, 버튼/예약=btn, 프로필=imgs+tp, 갤러리=imgs, Q&A=qbx+qp 등.
- **빌드 `builder.js`**: `FF(ff,f)` 폰트매핑·`box1(prims)` 텍스트병합·`pill()`·`ph()` 플레이스홀더·타입별 렌더 스위치. 모델 embed+빌더 → 단일 use_figma/템플릿.
- **검증**: 로그인 enabled 버튼 = `[...document.querySelectorAll('button')].find(x=>x.textContent.trim()==='로그인하기')` (Google 버튼도 포함 → `.trim()===` 정확매칭 필수). 에디터 진입 = `템플릿 사용하기` `$B click @e1`. 프리뷰 대기 = `overflow-y-scroll && left<130` 폴링.

### 1-4. 미해결/함정
- 로그인 세션 드롭 → `/onboarding` 튕김. 에디터 생성 API 400/409면 세션부터 확인.
- "템플릿 사용하기" = 매번 새 에디터 인스턴스 생성. 이번 생성분: **5018·5019·5020·5022·5023·5024**(분석용) → 정리 대상.
- GounBatang Figma 미보유 → KoPub Batang 대체. 미보유 서체 = 명조 Noto Serif KR/KoPub Batang, 고딕 Pretendard.
- Q&A 제출 버튼 box 미검출 시 흰색·중앙정렬 qp면 다크 pill 자동생성 보정. pill 텍스트색=버튼 bg 명도 자동(밝으면 검정)+`btn.tc` 우선.

---

## 2부 — vip-dinner 시안 · template-brief design-free 전환 · 에디터 이전 시도

> 작업 피그마: `2CX6W3Zg9OzbBiwIZ9Tk6J` (AI 워크플로우 리서치), 주요 프레임 **node 8-4333**.

### 2-A. template-brief 스킬 → design-free 단일 모드 통합
**산출물**: `.claude/skills/template-brief/` (SKILL.md·template.md 개정, `template-freeform.md` 삭제)
- 기존 2모드(기본=팔레트/폰트/카드옵션 고정 · freeform=자유) → **단일 design-free 표준** 통합.
- 근거: 외부도구(claude design·Stitch) 목적=**발산**. 브리프가 색·폰트·카드옵션·구성 묶으면 결과 수렴 → 무의미. CdBd 구조/옵션 매핑은 워크플로우 3단계에서 Claude가.
- 유지(불가침, 시각디자인 아님): 5대 원칙·가독성 3.6:1·14종 카드·규격·버튼글자=배경색·국문본문=한글폰트.

### 2-B. vip-dinner 시안 제작 여정 (node 8-4333)
1. **Claude 단일 시안** (Sanctuary 와인 `#371722`+샴페인 골드) — 5대원칙 정합 스켈레톤. claude design ABC + Stitch와 후보 풀 구성.
2. **채택 3안 부분 수정**: 프로토콜 오렌지 `#FF8906`→앰버골드 `#D9A441` · Classic Royal(Stitch)→네이비+골드(`#0f172a`/`#e2b87e`/`#1e293b`)+여백/텍스트 균형(64px→34, minHeight 해제 hug).
3. **8-4333(Sanctuary 복제) 대수술** (다회 정정): 네이비+골드 리컬러 · RSVP/Q&A 네이비 패널+골드보더 · 푸터 일회성 카피 · 모서리 각진 · Q&A/위치 카드화 · 골드 `#e2b87e`→`#E4C278`→`#CCA95F` 조정 · 섹션제목 영문대문자 28px 골드@80+짧은 밑줄 · **RSVP 슬롯 손그림 제거→예약 버튼 1개**(CdBd 예약카드 규칙 교정) · 제목+구분선 wrapper 해체(1요소=1카드) · **이미지 3장 gpt-image-1 생성·삽입**(헤더 연회장 3:2·호스트 한국 회장 1:1·좌석배치도 3:2, ~$0.18)·회장명 이정호.
- **의사결정 문서화**: DEC/RULE 형식 → RULE-1(포인트컬러 교체)·RULE-3(여백/사이즈 균형)만 가이드 반영 → [[../1. 작업 가이드/1-0. 템플릿 기획 워크플로우#🛠 채택 시안 수정 요청 처리 규칙 (2026-07-03 기록)]].

### 2-C. CdBd 에디터 이전(4단계) 시도 → 중단
- 로그인: "로그인하기" 텍스트 매칭이 "Google 계정으로 로그인하기" 오클릭 → OAuth 튐(이메일/비번은 세션 잔존 자동로그인).
- 색 picker: hex 입력 Enter 커밋이 "카드 추가" 모달 오픈 → 정확 네이비 `#0f172a` 미적용 → 다크+골드 프리셋 우회.
- blind JS 텍스트 클릭이 stray로 카드 오염(5026에 2단·예약 카드 임의 추가).
- **🔴 근본 원인 = 공유 browse 데몬**: 다른 에이전트가 같은 browse Chromium으로 5025 작업 중 → 내 `$B`가 그쪽 탭 충돌 → 5025 에러 반복. **중단.** → 영구기록 [[../CLAUDE.md#🚫 CdBd 에디터 동시 작업 금지 (같은 계정 · 2026-07-03 확인)]].

---

## 3부 — interior-portfolio 멀티페이지 브리프 · claude design 시안 3종 이전

> `interior-portfolio`(홍보·카탈로그, **멀티페이지 BETA**)를 신 시안 생성 파이프라인(2026-07-03 개정)으로 재출발. 진입점: 구 스켈레톤 [figma 590:23](https://www.figma.com/design/oi8zIHLfy59O5zV8aysqq4/CdBd-%ED%85%9C%ED%94%8C%EB%A6%BF-%EB%93%B1%EB%A1%9D?node-id=590-23) ("구성은 좋다, 신 워크플로우로 재출발").

### 3-1. 멀티페이지 브리프 개정 (`template.md` 3개 장)
- **0장 본질** — "멀티페이지" 개념: 링크된 페이지(각=독립 세로 카드 스택)+이동 2경로(빌더 제공 ☰ 페이지메뉴=앱크롬 금지의 예외 / 표지 인덱스 버튼카드). 원칙#1에 "시공 사례 페이지=사용자가 통째로 복제하는 반복단위" 추가.
- **4장 요소** — 페이지 단위(표지/소개/시공사례/견적) 그룹핑. 페이지 안 순서·카드는 개방.
- **5장 결과물** — 시안 3종 각각 페이지 4종 가로 렌더(사례는 대표 1개+"복제로 추가" 주석), 전 페이지 색·폰트 일관성 요구.
- **3장 규격** — 멀티페이지(BETA)·권장 페이지수(4~6)·BEFORE/AFTER 비율통일 행 추가.
- 🔧 후속: 멀티페이지 개정을 `template.md`에 상수 반영할지(멀티페이지 5개=interior·startup·corporate-sales·trade-show·beauty → 스킬 내장 유리).

### 3-2. HTML 시안 → 피그마 이전 (재사용 절차)
- **claude design "bundled page" 포맷**: 20MB·gzip asset + shadow DOM → innerText 추출 불가 → **스크린샷 캡처가 정답**.
- **헤드리스 렌더 (browse)**: `file://`는 cwd/$TMPDIR 스코프 → `cp ~/Downloads/x.html /tmp/` 후 `goto file:///tmp/x.html`. self-unpack 5~6초 sleep. viewport 크게(1720×1700)+행별 scroll.
- **행·열 좌표 결정적 태깅** (DOM 순서 태깅 X — 리로드마다 불안정+중첩 380프레임 오정렬): 3행(y A≈329·B≈2451·C≈4546)×4열(x=64·480·896·1312), 380폭 h>400 & 부모도 380폭인 요소 중 셀별 최상단·최대높이 하나 → `data-pg=A1..C4`. scale 1로 안정 캡처(2x 재태깅은 리플로우 실패).
- **피그마 배치**: Section+RECTANGLE 12개(정확 좌표) → `upload_assets(count=1,nodeId=RECTANGLE,scaleMode=FILL)` 반환 submitUrl에 curl POST. auto-layout FRAME 자동fill 실패 회피=RECTANGLE 타겟. SectionNode엔 `resizeToFit()` 없음→`resizeWithoutConstraints`. get_screenshot(Section)=원점(0,0) 프레이밍 아티팩트→get_metadata authoritative.

**재사용 스니펫 (행·열 결정적 태깅)**
```js
const rowsY={A:329,B:2451,C:4546}, colsX={1:64,2:480,3:896,4:1312};
const cand=[];
document.querySelectorAll('*').forEach(e=>{
  if(e.offsetWidth===380 && e.offsetHeight>400){
    const p=e.parentElement; if(!(p&&p.offsetWidth===380))return;
    const r=e.getBoundingClientRect();
    cand.push({e, x:r.left+scrollX, y:r.top+scrollY, h:e.offsetHeight});
  }
});
for(const rk in rowsY)for(const ck in colsX){
  const inCell=cand.filter(c=>Math.abs(c.x-colsX[ck])<6 && c.y>rowsY[rk]-10 && c.y<rowsY[rk]+300);
  if(inCell.length){ inCell.sort((a,b)=>b.h-a.h); inCell[0].e.setAttribute('data-pg', rk+ck); }
}
```

### 3-3. 시안 3종 스펙 (claude design 산출 · 보드 [948:32](https://www.figma.com/design/oi8zIHLfy59O5zV8aysqq4/CdBd-%ED%85%9C%ED%94%8C%EB%A6%BF-%EB%93%B1%EB%A1%9D?node-id=948-32))
| 시안 | 무드 | 배경/텍스트/버튼 | 폰트 | 모서리 | 본문대비 | 가상 브랜드 |
|---|---|---|---|---|---|---|
| **A** | 고요한 갤러리 | `#F7F6F3 / #191919 / #191919` | Noto Serif KR + 프리텐다드 | 각진 | 16.21 AAA | 여백(YEOBAEK STUDIO) |
| **B** | 따뜻한 결 | `#F6F0E6 / #40342A / #7A5C3E` | 고운바탕 + 나눔고딕 | 둥근(r16) | 10.71 AAA | 온재하우스 |
| **C** | 구조적 대담 | `#17191E / #F2F0EA / #D96C3F` | 프리텐다드 + Montserrat | 다크 | 16.51 AAA | 단면공간 |
- 페이지 4종 흐름: 표지(인덱스·이동버튼)→소개(프로필·인용·실적 3개·시공분야·상담)→시공사례(제목·메타·BEFORE/AFTER·사양·스토리·상담)→견적(공간유형·평형·예산·시기·성함·연락처 Q&A+무료견적버튼+위치·상담).

---

## 4부 — interior-portfolio 여백-스케일 CdBd 시안 직접 제작 + 내추럴 무드 (본 세션)

> **산출물**: 피그마 새 섹션 **node `947:23`** (원본 스켈레톤 590:23 우측). 5페이지 멀티페이지, 내추럴 무드 적용 완료.
> 3부의 claude design 3종 파이프라인과 **별개 경로** — 외부도구 없이 **Claude가 CdBd 카드 구조로 직접 use_figma 빌드**(신 워크플로우 3단계를 외부시안 없이 처음부터 직접 수행한 케이스).

### 4-1. 결정 흐름
1. 사용자: 590:23(구 스켈레톤) 콘텐츠 기반 "**시안 1개 제작, 오늘 새 규칙(여백 스케일) 특히 반영**".
2. 1차 산출 = **디폴트 테마 스켈레톤**(fafafa/292929/프리텐다드)으로 만듦 → 사용자 정정: "**무드 적용한 시안을 원했다**" → 2차로 무드 적용.
3. 무드 선택은 taste 결정 — AskUserQuestion 도구가 internal error로 실패 → 되묻지 않고 **브랜드 최적 무드(내추럴) 직접 선정** + 대안(모던시크 라이트/다크) 즉시교체 제안.

### 4-2. 시안 스펙 (947:23 · 5페이지)
- 표지(hero full-bleed·회사명·슬로건·목차버튼3) / 소개(헤더·대표프로필·성과밴드·시공분야·상담2버튼) / 시공사례①②(제목·보조·BEFORE/AFTER 갤러리·시공정보밴드·스토리·상담) / 견적(CTA·Q&A폼·위치안내·시공가능지역·상담).
- **오늘 여백 스케일 전면 적용**: side 28 · 헤더 320 · 갤러리 222 · 섹션간 26~32 · 버튼 내부 pt/pb18 · 첫카드 pt38·마지막 pb42 · 보조텍스트 55~80% 투명도.
- **단일 depth 예외**(배경없는 카드 wrapper 없이 단일 padding) · 배경있는 카드(성과·시공정보 밴드)만 2-depth · **버튼글자=배경색**(filled) · **텍스트 속성 분리**(제목/보조/본문 개별 카드).

### 4-3. 무드 적용 (2차)
- 🌿 **내추럴/오가닉 · HappyHues 8**: 배경 `#F8F5F2` / 텍스트 `#232323` / 버튼(포인트) `#078080` 틸 · **대비 14.47 AAA** · 폰트 프리텐다드(내추럴 호환).
- CdBd 테마 매핑: **filled 버튼**(무료견적·지도이동)=틸 bg+배경색 글자 / **outlined 버튼**(목차·전화·카톡)=틸 stroke+틸 글자 / 밴드=텍스트색 6%.

### 4-4. 재사용 기법 — 색 시그니처 기반 리컬러
- 디폴트 테마 스켈레톤을 무드로 바꿀 때, 노드 순회하며 solid fill/stroke의 color를 **시그니처로 매칭 remap**: `0.98→배경 · 0.886→플레이스홀더 · 0.161→텍스트색`(투명도 보존). filled/outlined 버튼은 이름(`filled`/`btn`+stroke)으로 **선분류** 후 버튼색 적용.
- 효과: **디폴트 스켈레톤 1개 만들어두면 무드만 갈아끼워 N개 배리에이션 생성**. (모던시크 라이트/다크로 즉시 재적용 가능.)

### 4-5. 미해결/함정
- 🔴 **Figma Section 자식 = 상대좌표**: 섹션에 appendChild 후 `child.x`에 절대좌표 넣으면 (섹션원점+값) 이중 오프셋 → 페이지가 멀리 튐. **child.x/y는 섹션 원점 기준 상대값**으로. (get_metadata의 x/y=상대, absoluteBoundingBox=절대.) → CLAUDE.md 자동화 함정 승격 후보.
- 무드 확정 대기 — 내추럴 vs 모던시크(라이트/다크). 확정 후 3단계(실사 이미지 gpt-image-1)→4단계(에디터 이전).

---

## 다음 세션 진입 우선순위 (통합)

1. **interior-portfolio 경로 정리** — 두 산출물 병존: (a) claude design 3종 `948:32` 중 선정/재조합(구조·무드 분리) → CdBd 재구성, (b) 여백-스케일 직접빌드 시안 `947:23` 무드 확정. **어느 경로로 최종 갈지 사용자 방향 필요.**
2. **947:23 후속**: 무드 확정(내추럴 vs 모던시크) → 실사 이미지 채움(gpt-image-1) → 4단계 에디터 이전. 필요 시 3-0 §4.5에 947:23 링크 추가.
3. **template-brief 멀티페이지 모드 상수화** — 멀티페이지 5템플릿 대비 스킬 내장 검토.
4. **라이브 18개 재현 잔여** — 초대·예약 7번(수강신청·반별예약) → 홍보·카탈로그(4) → 프로필·명함(7). 파이프라인 `.data/live-editor-structures/`. 멀티페이지는 페이지별 반복추출 유의.
5. **vip-dinner 에디터 빌드 재개** — 조건: browse 단독점유. 스펙=node `8-4333`. 5026 잘못추가 카드 정리 + 정확 네이비 hex(`#0f172a`) 적용법(색picker RGB 필드 직접 입력 시도). blind JS ❌ → snapshot @ref.
6. **분석용 에디터 인스턴스 정리 컨펌** — 5018·5019·5020·5022·5023·5024(재현) + 5025·5026(vip-dinner). CLAUDE.md TODO 반영.

## CLAUDE.md / 가이드 승격 후보 (사용자 승인 시)
- **자동화 함정 표** 추가 5건: ① browse `file://` cwd/tmp 스코프 ② `upload_assets` Section/RECTANGLE fill + `resizeWithoutConstraints`(Section엔 resizeToFit 없음) ③ get_screenshot(Section) 원점 프레이밍 아티팩트 ④ **Figma Section 자식 상대좌표 이중오프셋** ⑤ **색 시그니처 기반 리컬러(무드 배리에이션 생성 기법)**.
- **워크플로우 3단계 보강** ([[../1. 작업 가이드/1-0. 템플릿 기획 워크플로우]]): "외부도구 bundled HTML→헤드리스 캡처→피그마 이미지보드"(3부) + "디폴트 스켈레톤 직접빌드→색 시그니처 리컬러로 무드 배리에이션"(4부).
- 라이브 재현 빌드 아키텍처는 이미 [[../2. CdBd 템플릿 현황/.data/live-editor-structures/_index.md]]에 영구 기록됨.
