---
name: CdBd 템플릿 디자인 시스템
description: 비디자이너용 모바일 비즈니스 페이지 템플릿 — 테마 변수 · 9무드 · 평면 카드 스택
colors:
  theme-bg-default: "#FAFAFA"
  theme-ink-default: "#292929"
  theme-button-default: "#292929"
  accent-natural: "#078080"
  accent-feminine: "#CF2F89"
  accent-luxury: "#F9BC60"
  accent-professional: "#0B64FE"
  accent-modern: "#7F5AF0"
  accent-vivid: "#FF8906"
  accent-vintage: "#8C7851"
  accent-fun: "#FFD803"
  accent-dreamy: "#F582AE"
typography:
  display:
    fontFamily: "Pretendard, sans-serif"
    fontSize: "40px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Pretendard, sans-serif"
    fontSize: "28px"
    fontWeight: 700
    lineHeight: 1.3
  title:
    fontFamily: "Pretendard, sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "Pretendard, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Pretendard, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
rounded:
  sharp: "0px"
  round: "16px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "16px"
  md: "24px"
  lg: "40px"
components:
  button-primary:
    backgroundColor: "{colors.theme-button-default}"
    textColor: "{colors.theme-bg-default}"
    rounded: "{rounded.round}"
    padding: "18px 24px"
    height: "58px"
  card:
    backgroundColor: "transparent"
    rounded: "{rounded.round}"
    padding: "{spacing.md}"
  card-tinted:
    backgroundColor: "{colors.theme-bg-default}"
    rounded: "{rounded.round}"
    padding: "{spacing.md}"
  qa-input:
    backgroundColor: "transparent"
    textColor: "{colors.theme-ink-default}"
    rounded: "8px"
    padding: "12px 10px"
---

# Design System: CdBd 템플릿

> 전략(누가·무엇·왜)은 [[PRODUCT.md]]. 이 문서는 시각(어떻게 보이는가)만 다룬다.
> 색상·폰트 원본 라이브러리: [[1. 작업 가이드/1-2. 색상 팔레트]] · [[1. 작업 가이드/1-3. 폰트]] · 카드 스펙: [[1. 작업 가이드/1-5-2. CdBd 카드 기능]].

## 1. Overview

**Creative North Star: "교체 가능한 카드 키트 (The Swappable Card Kit)"**

CdBd 템플릿의 모든 요소는 **비디자이너 사업자가 복제·삭제·재색칠할 수 있는 카드**다. 완성된 예술품이 아니라, 사용자가 몇 분 만에 자기 것으로 바꾸는 **출발점**이다. 그래서 이 시스템의 시각적 결정은 전부 "이걸 사용자가 쉽게 바꿀 수 있는가"를 첫 질문으로 통과한다. 멋짐과 편집 용이성이 충돌하면 편집 용이성이 이긴다.

색은 실제 hex가 아니라 **세 개의 테마 변수**(`{배경색}`·`{텍스트색}`·`{버튼색}`)로 존재한다. 사용자가 9개 무드 중 하나를 고르면 팔레트와 폰트가 **동시에** 결정되고, 페이지 전체가 그 톤을 따라간다. 보조 톤은 별도 색이 아니라 `{텍스트색}×N%`·`{버튼색}×N%` 투명도로 파생된다 — 테마를 바꿔도 자동으로 따라오게.

이 시스템이 **명시적으로 거부하는 것**: 사용자가 CdBd 에디터에서 바꿀 수 없는 **편집 불가 장식(팬텀 그래픽)** — 골드 라인·점선 테두리·노치·형광펜; **한 카드에 여러 텍스트 속성 묶기**; opacity-blended 유효색·픽셀 패딩 매칭 같은 **시안 단계 미세 위계**; 유튜브 플레이·별표·지도 임베드처럼 **카드가 이미 제공하는 default 기능을 다시 그리는 것**; 보조 텍스트를 별도 회색 hex로 지정하는 것.

**Key Characteristics:**
- **평면 카드 스택** — 그림자·중첩 컨테이너 없음. 깊이는 섹션 배경 띠와 여백으로만.
- **테마 변수 3역할** — `{배경색}`·`{텍스트색}`·`{버튼색}`. 한 번에 톤 교체.
- **9무드 통일** — 색과 폰트가 같은 무드 축에서 동시 결정.
- **1 카드 = 1 속성** — 카드를 지워도 레이아웃이 무너지지 않는다.
- **카드 default 신뢰** — 기본 제공 UI·동작은 디자인에서 재현하지 않는다.

## 2. Colors: 테마 변수 위의 9무드

색은 고정 팔레트가 아니라 **역할 토큰 3개** 위에서 무드별로 교체된다. 기본(스켈레톤) 테마는 의도적으로 무채색이며, 색 정체성은 사용자가 고른 무드에서 온다.

### Primary
- **버튼/액센트 (`{버튼색}`, 기본 #292929)**: 모든 액션(버튼·CTA)과 헤드라인 포인트 컬러. 무드마다 이 슬롯이 그 무드의 시그니처 색으로 바뀐다(아래 인덱스). 버튼 텍스트는 항상 `{배경색}`으로 렌더된다.

### Neutral
- **배경 (`{배경색}`, 기본 #FAFAFA)**: 페이지·카드 바탕. 무드의 가장 넓은 면.
- **텍스트 (`{텍스트색}`, 기본 #292929)**: 본문·제목. 보조 텍스트는 `{텍스트색}×60%` 또는 `×40%` 투명도로 파생.

### 9무드 팔레트 인덱스 (대표 팔레트 1개씩 · 전체 70개는 라이브러리 노트)
| 무드 | 배경 | 텍스트 | 버튼/액센트 | 대비 |
|---|---|---|---|---:|
| 🌿 내추럴/오가닉 | `#F8F5F2` | `#232323` | `#078080` | 14.47 AAA |
| 🌸 페미닌/로맨틱 | `#DABAAF` | `#0B0C11` | `#CF2F89` | 10.81 AAA |
| ✨ 럭셔리/엘레강스 | `#004643` | `#FFFFFE` | `#F9BC60` | 10.72 AAA |
| 💼 프로페셔널/비즈니스 | `#F2F2F2` | `#000000` | `#0B64FE` | 18.76 AAA |
| 🌑 모던/시크 | `#16161A` | `#FFFFFE` | `#7F5AF0` | 18.03 AAA |
| 🔥 비비드/대담한 | `#0F0E17` | `#FFFFFE` | `#FF8906` | 19.16 AAA |
| 🎨 빈티지/노스탤직 | `#F9F4EF` | `#020826` | `#8C7851` | 18.04 AAA |
| 🎉 펀/플레이풀 | `#FFFFFE` | `#272343` | `#FFD803` | 14.91 AAA |
| 🌙 드리미/감성적 | `#FEF6E4` | `#001858` | `#F582AE` | 15.35 AAA |

### Named Rules
**The Theme-Variable Rule.** 색은 언제나 `{배경색}`·`{텍스트색}`·`{버튼색}` 세 역할로만 지정한다. 하드코딩 hex 금지 — 사용자가 무드 하나를 바꾸면 페이지 전체가 따라와야 한다.

**The 3.6:1 Rule.** 배경↔텍스트 대비는 **≥ 3.6:1**(햇빛·작은 화면 전제, AA-Large 3:1보다 엄격). 본문은 가능하면 4.5:1까지 밀어붙인다. 3.6~4.5 등급 팔레트는 긴 본문 대신 헤드라인·CTA에.

**The Button-Contrast Rule.** 버튼 텍스트 = `{배경색}` 고정 매핑이므로, `{버튼색}`은 `{배경색}` 대비 **≥ 3.6:1**이어야 글자가 읽힌다. 팔레트의 "텍스트-배경 대비"만 보면 놓친다 — 버튼-배경 대비는 별도로 검증하라.

**The Transparency-Not-Gray Rule.** 보조 텍스트(캡션·유의사항)는 별도 회색 hex가 아니라 `{텍스트색}×N%`. 섹션 강조 배경 톤은 `{버튼색}×N%`(텍스트색 ❌) — 액센트가 따라와 섹션 구분이 또렷해진다.

## 3. Typography: 한 페이지 1~2개, 무드가 고른다

**Display Font:** 무드별 헤드라인 폰트 (기본 Pretendard) · **Body Font:** 무드별 본문 한글 폰트 (안전 폴백 Pretendard)

**Character:** 폰트도 색과 같은 9무드 축에서 결정된다. 헤드라인은 무드의 개성(명조·손글씨·지오메트릭)을, 본문은 가독성을 맡는다. 기본 스켈레톤은 Pretendard 단일 — 어떤 무드에서도 실패하지 않는 폴백.

### Hierarchy
- **Display** (Bold 700, 40px, 1.2, letter-spacing -0.02em): 페이지 최상단 타이틀·로고 타이포. 무드 디스플레이 폰트.
- **Headline** (Bold 700, 28px, 1.3): 섹션 제목. 포인트 컬러(`{버튼색}`) 액센트 허용.
- **Title** (SemiBold 600 / 강제 Bold, 20px, 1.4): 카드 제목·소제목.
- **Body** (Regular 400, 16px, 1.6): 본문. 국문은 한글 폰트 의무. 모바일 1열이라 line-length는 자연히 짧음.
- **Label** (Regular 400, 14px, 1.5): 보조·캡션. 색은 `{텍스트색}×60%`.

> CdBd 실제 사이즈 스텝: 12·14·16·18·20·22·24·26·28·30·35·40·45·50·55·60 / 줄간격 100·110·120…%(10% 단위). 이 범위 밖 임의값 ❌.

### Named Rules
**The One-or-Two-Font Rule.** 한 페이지 = 1~2개 폰트. 기본 1개(전체 통일), 헤드라인+본문 분리 시에만 2개. 그 이상은 이미지(로고)로 처리.

**The Korean-Body Rule.** 국문 본문·캡션·버튼 텍스트는 **반드시 한글 폰트**. 영문 폰트로 한글 본문을 쓰면 fallback 렌더링이 깨진다. 장식용 영문 헤드라인 + 한글 본문 조합만 예외 허용.

**The Display-Never-Body Rule.** 헤드라인 전용(🆑) 19종(마포꽃섬·G마켓산스·베이글팻·Playfair Display 등)은 **본문 금지**. 본문은 🅰 본문 전문 / 🅱 전천후 등급만.

**The Forced-Bold Rule.** 고운돋움·마포꽃섬처럼 Regular만 있는 싱글웨이트 폰트도 CdBd 에디터에서 **강제 Bold 토글** 가능 — 헤드라인·버튼 텍스트(≥14px)는 Bold 처리 대상으로 기록하라.

### 9무드 대표 폰트 조합 (헤드라인 / 본문)
🌿 Quicksand / 고운돋움 · 🌸 Playfair Display / 본명조 · ✨ Playfair Display / KoPub바탕 · 💼 프리텐다드 / 프리텐다드 · 🌑 Montserrat / 프리텐다드 · 🔥 Bebas Neue / 프리텐다드 · 🎨 Libre Baskerville / 부크크명조 · 🎉 HS산토끼체 / 고운돋움 · 🌙 Zeyada / 고운바탕

## 4. Elevation: 평면 스택

이 시스템은 **그림자를 쓰지 않는다.** CdBd 페이지는 중첩 그룹 컨테이너 없는 **평면 카드 스택**이다. 깊이·구분은 세 가지로만 표현한다: (1) **섹션 배경 색 띠** — 여러 카드에 동일 `{배경색}`을 주고 외부여백 0으로 맞붙여 연속 띠를 만든다, (2) **카드 내부/외부 여백**, (3) **구분선 카드**(두께 0의 여백 카드 포함). 그래서 어떤 화면도 카드가 위로 떠오르지 않고, 종이 위에 붙은 조각들처럼 평평하다.

### Named Rules
**The Flat-Stack Rule.** 페이지는 페이지 프레임의 직계 자식 카드들이 위→아래로 쌓인 평면 스택이다. `box-shadow`·글래스모피즘·중첩 카드 **금지**. 깊이가 필요하면 그림자가 아니라 섹션 배경 띠와 여백으로.

**The No-Auto-Gap Rule.** CdBd엔 자동 분배 레이아웃(`SPACE_BETWEEN`/`SPACE_AROUND`)이 없다. 카드 간격은 각 카드의 상하 padding 또는 여백 카드로만. 가로 N등분은 등폭 FILL + 고정 간격(2단 카드).

## 5. Components

카드 15종 시스템. 각 카드는 페이지 프레임의 직계 자식(top-level)이며, 다른 속성·타입은 절대 한 카드로 묶지 않는다("평탄화").

### Buttons
- **Shape:** 각진(0px) / 둥근(16px) / 원형(999px) 3가지 옵션만. 픽셀 임의값 ❌.
- **Primary:** 배경 = `{버튼색}`(채움), 텍스트 = `{배경색}`. 높이 ~58px.
- **금지:** 위치 안내 카드 버튼을 테두리만 있는 outline으로 만들지 말 것(채움 고정). 단일 SNS 강조는 버튼 카드(SNS 카드는 푸터 전용).

### Inputs / Fields (Q&A 카드 = 범용 폼)
- **주관식 입력:** border 1px `{버튼색}` · radius 8px · padding 12/10px · placeholder `{텍스트색}×50%`.
- **객관식 마커:** 라디오 20×20 · 체크박스 16×16 · 마커-옵션 gap 12 — **CdBd 시스템 자체 디자인**, 시안에서 임의 변경 ❌.
- **조정 가능 옵션은 3가지뿐:** 텍스트 크기 / 정렬 / 질문 간 간격(16·24·32·40).
- **제목은 무조건 중앙정렬, 제출 버튼은 카드 하단 내장**(별도 버튼 카드 ❌).

### Cards / Containers
- **Corner:** 각진 / 둥근 / 원형(위 shape와 동일 3옵션).
- **Background:** 투명 또는 `{배경색}`. 섹션 띠는 인접 카드에 같은 배경 + 외부여백 0.
- **Shadow:** 없음(§4 Flat-Stack).
- **Internal Padding:** 0~40px(2단위 21스텝). 4면 비슷하게, 최소 상=하 대칭(카드 삭제 시 균형 유지).
- **External Padding:** 배경/테두리 있는 카드만 wrapper로 별도. 배경·테두리 없는 카드는 단일 depth padding 하나만.

### 텍스트 카드 (Signature)
1 카드 = 1 텍스트 속성. "제목+본문", "본문+보조설명"은 항상 별도 카드로 분리. 인라인 속성 혼합 불가.

### 프로필 (Signature)
이미지 + **텍스트 2개만(이름 + 소개글)**, 셋째 줄 ❌. 요소 gap 고정(기본·강조형 32 / 명함형 28). 이미지 크기는 `innerStyle.width %`로.

### 갤러리 / 위치 안내 / 메뉴 / 2단 카드
- **갤러리:** 그리드 column 수 · borderRadius · gap(0~40, 4단위). 기본 그리드는 카드 default — 재현 ❌.
- **위치 안내:** 지도+주소가 한 단위. 주소 = 단일 텍스트 속성 + 중앙정렬 전용. 제목은 위 별도 텍스트 카드로. "지도 보기" 버튼은 주소를 검색 드롭다운에서 선택(지오코딩)해야 동작.
- **메뉴:** default 액션(전화·문자·이메일·vCard) 묶음에 적합.
- **2단 카드:** 2~4분할 등폭 FILL + 내부 텍스트/이미지/버튼/예약 삽입. 다중 버튼 그리드의 대안.

## 6. Do's and Don'ts

### Do:
- **Do** 색을 `{배경색}`·`{텍스트색}`·`{버튼색}` 세 변수로만 지정하고, 보조 톤은 투명도(`×N%`)로 파생시켜라.
- **Do** 버튼 텍스트를 `{배경색}`으로 두고, `{버튼색}`이 `{배경색}` 대비 ≥3.6:1인지 별도로 검증하라.
- **Do** 하나의 텍스트 카드에 하나의 속성만 담아 — 사용자가 카드를 지워도 균형이 유지되게.
- **Do** 카드가 기본 제공하는 UI·동작(유튜브 플레이·별표·지도 임베드·갤러리 그리드)은 그대로 신뢰하고 디자인에서 다시 만들지 마라.
- **Do** 모서리는 각진/둥근/원형, 여백은 0~40(2단위), 텍스트는 정해진 사이즈 스텝 안에서만 조정하라.
- **Do** 국문 본문엔 한글 폰트를, 한 페이지엔 1~2개 폰트만 써라.

### Don't:
- **Don't** 사용자가 못 바꾸는 편집 불가 장식(팬텀)을 넣지 마라 — 골드 라인·점선 테두리·노치·형광펜. 강조는 포인트 컬러·섹션 배경·텍스트 위계로만.
- **Don't** 보조 텍스트를 별도 회색 hex로 지정하지 마라 — `{텍스트색}×N%` 투명도로.
- **Don't** opacity-blended 유효색·픽셀 패딩 매칭·SemiBold/Medium 미세 구분 같은 시안 단계 미세 위계를 만들지 마라.
- **Don't** 자동 분배 레이아웃(`SPACE_BETWEEN`/`SPACE_AROUND`)이나 그림자·글래스·중첩 카드를 쓰지 마라(§4).
- **Don't** 헤드라인 전용 폰트로 본문을 쓰거나, 영문 폰트로 한글 본문을 쓰지 마라.
- **Don't** 위치 카드 버튼을 outline으로, 예약카드 옵션을 "풀패키지" 같은 SKU 어휘로 부르지 마라.
- **Don't** (impeccable 공통) side-stripe border(1px 초과 색 띠 테두리)·gradient text·장식용 글래스모피즘을 쓰지 마라.
