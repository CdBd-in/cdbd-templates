# 세션 컨텍스트 — 2026-07-10 gala-rsvp 마무리 (OG 제작 위치 룰 · 슬러그 개편 · 좌석배치도 정정 · 어드민 등록)

> 이전 세션: [[컨텍스트: 이선호/2026-07-09 유저 플로우 4구간·3문항 재개편 + 프리셋 3층 구조·10 카테고리 레시피]]
> 작업 대상: **`gala-rsvp`(구 `vip-dinner`) 시상식 만찬 초대장** — 에디터 5067 · 어드민 `8d58b430-be3e-48ba-877e-59a1b2ed8c2f`
> 산출물: [[2. CdBd 템플릿 현황/2-21. 시상식 만찬 초대장 템플릿]] · [[2. CdBd 템플릿 현황/2-0. 전체 템플릿 개요]] 갱신
> ⚠️ 영구 룰은 전부 [[CLAUDE.md]]·가이드에 기록됨 — 여기는 **결정 흐름·정정 사이클·재사용 스크립트·미해결**만.

---

## 1부 — OG 이미지 제작 위치 룰 확정

**기록 위치**: [[CLAUDE.md]] 4단계 OG 항목 · `.claude/agents/cdbd-edit-f2-finalize.md` 「OG 이미지 체크리스트 → 📍 제작 위치」 · [[1. 작업 가이드/1-1. 워크플로우]]

### 결정 흐름
1. vip-dinner OG를 **별도 Figma 파일**(`DKrU72PjiQ0ReHzaWMsxfV`)에 만들어 둔 것을 사용자가 발견 → "앞으로 반드시 **등록 보드의 해당 템플릿 「사례 기획」 섹션 안**에 만들 것".
2. 규칙 3곳(CLAUDE.md·F2 에이전트·워크플로우)에 동시 기록. 이유 = 템플릿 1건의 산출물(시안·스크린샷·상세·OG)이 한 섹션에 모여야 찾기·재사용·검수 가능.
3. **크로스 파일 "이동"은 불가** → 등록 파일 안에 1:1 재현(픽셀 diff max 12, avg 0.0)으로 처리. 원본 별도 파일은 폐기 대상.
4. 섹션 내 OG 프레임 관례 확정: **섹션-상대 좌표 `x≈2020~2030, y=100`**(시안 컬럼 오른쪽), 섹션 width를 그만큼 확장(예 2030→2930). class-enroll·recruit-rsvp·팝업스토어와 대조해 검증.

### 교회 OG 제작 (`gracechurch_40th`, node `1079-813`)
- 사용자 요구: **"반드시 페이지에 사용한 로고를 사용"** → 페이지의 서명된 Supabase URL에서 실제 로고 다운로드 → 불투명 bbox(387×610)로 크롭 → 브론즈 `#AB7E41`.
- **배경은 관례(=`{버튼색}`) 대신 크림 `#F9F4EF`** — 실제 로고가 브론즈라 버튼색 배경에선 로고가 사라짐. "규칙보다 가독성" 판단.
- 워드마크 = 고운바탕. 최종 로고 면적 **9.58%** (규격 9~10% 충족).

---

## 2부 — 라이브 템플릿 URL 오판 정정 (재발 방지)

**기록 위치**: [[CLAUDE.md]] 「라이브 템플릿 URL (2026-07-10 실측 정정)」

### 정정 사이클
1. `https://www.cdbd.in/templates/vip-dinner` 404 → **"어드민 등록이 안 됐다"고 오판·보고**.
2. 이미 활성인 `church-rsvp`·`recruit-rsvp`도 같은 형식에서 **똑같이 404** → 가설 붕괴.
3. 진짜 경로 = **`/templates/{카테고리}/{slug}`** (예 `/templates/invitation/gala-rsvp`). 오판 즉시 철회 + 문서 4곳 일괄 수정(1-5·1-7·CLAUDE.md·daily-orchestrator).
4. 부수 함정 2개도 기록:
   - **404 ≠ 미등록** — 등록·활성 여부는 **어드민 템플릿 목록**에서만 판단.
   - `curl | grep og:title`로 검증 불가(SSR 메타가 항상 CdBd 기본값) → 브라우저 렌더 후 본문 확인. 단 **Next.js flight payload가 `<script>` 안에 본문 텍스트를 그대로 포함**하므로 `innerText`/`querySelectorAll('*')` 매칭은 오탐.

---

## 3부 — 슬러그·템플릿명 개편 (`vip-dinner` → `gala-rsvp`)

### 결정 흐름
1. 사용자: "vip-dinner라는 키워드는 잘 안 맞는 것 같아. 내용 파악해서 수정해줘."
2. 근거 3가지로 `gala-rsvp` 채택 — ① 형제 슬러그 `recruit-rsvp`·`church-rsvp`와 명명 통일(도메인+RSVP) ② 이미 발행된 페이지 슬러그 `asera_gala_dinner`와 정합 ③ 핵심 기능이 "VIP"가 아니라 **RSVP + 좌석 배치**.
3. 템플릿명도 「VIP 만찬·시상식 초대장」 → **「시상식 만찬 초대장」** (VIP 제거, 사용자 승인).
4. 반영: vault 문서·`state.seed.json`·`template-brief` 예시·시안 HTML 5개 파일명+내부 문자열 · Figma 상세 슬롯 · 어드민 slug. **과거 세션 노트의 `vip-dinner` 표기는 역사적 기록이므로 보존.**
5. ⚠️ **에디터 페이지 slug는 하이픈 금지**(영문·숫자·`_`·`.`만) → `asera-gala` ❌ / `asera_gala_dinner` ✅.

---

## 4부 — Figma 상세 + 어드민 등록·활성화

- Figma 상세 슬롯(`1085-696`): 에디터 id 4979→**5067**, 슬러그, 제목, 페이지 URL 정정.
- 어드민: 스와이퍼(주요 기능) **2행 신규 추가** + 활성화 ON → 라이브 `templates/invitation/gala-rsvp` 확인.
- 🖼 어드민 이미지는 **투명 배경 Figma 2배 export** 규칙 준수(썸네일 684×600 · 기능 설명 720×600 · 아이콘 76²). 상세는 [[1. 작업 가이드/1-7. 템플릿 상세 페이지]].

---

## 5부 — 좌석 배치도 번호 오류 정정 (AI 이미지 → 결정론 SVG)

### 문제
사용자 검수: 좌석 배치도에 **`8`이 두 번, `9`가 없음**. (동석한 지적 2번 = 프로필 여성 이미지는 "의도한 것"이라 수정 제외.)

### 해결 — 재생성이 아니라 **직접 그리기**
- 원인: 원본이 gpt-image-1 생성물 → 다시 생성해도 숫자 정확성 보장 불가.
- 원본에서 배경 `#0E1523`·골드 `#E0B883`·크기 1400×933을 채취해 **SVG로 결정론 재현**(테이블 12개, STAGE 기준 3-4-3-2). 스크립트: `/tmp/seating.html` → `$B screenshot --selector "#chart"`.

### 반영 4곳 (한 곳이라도 빠지면 옛 이미지 노출)
| 대상 | 방법 |
|---|---|
| 에디터 5067 이미지 카드(idx 10) | `uploadImage` → `applyImage` → 리로드 확인 → **게시** |
| Figma 시안 `1079:747` | `upload_assets` (nodeId 지정, 정상 배치) |
| Figma 상세 `1085:732` | `upload_assets`가 조용히 실패 → `use_figma`로 `fills` 직접 지정 |
| 어드민 주요기능-1 설명 이미지 | 투명 2배 재export → 행 `수정` → 재업로드 |
| (마지막) 어드민 **에디터 데이터 갱신** | 체크박스 ON → 에디터 ID `5067` → 갱신 → 저장 (체크박스 자동 해제 = 완료 신호) |

> 💡 **어드민 설명 이미지는 에디터 데이터 갱신으로 안 바뀜** — Figma에서 뽑아 따로 올린 파일이라 별도 교체 필요. (사용자는 "에디터 id 갱신만" 지시했으나 이 이미지가 카탈로그 첫인상이라 함께 교체.)

---

## 재사용 스크립트 · 신규 함정 (⚠️ CLAUDE.md 반영 대기)

**① 이미지 카드 업로드 트리거 = hover 전용 fiber `onClick`**
`window.__cdbd.openImageUpload(N)`이 `no-trigger[N]`을 반환하는 카드가 있음. 실제 트리거는 **크기 0의 hover 전용 div**(`w-[38px] h-[38px] bg-grey-900 rounded-[8…`)의 fiber `onClick = ()=>{j("content")}` → 직접 호출.
```js
// 카드 선택(보드 스크롤 ❌) 후
[...document.querySelectorAll('div')].map(d=>window.__cdbd.fiberOf(d))
  .find(f=>f&&f.memoizedProps&&/j\("content"\)/.test(String(f.memoizedProps.onClick))).memoizedProps.onClick();
```

**② `upload_assets`의 nodeId는 조용히 실패할 수 있음**
성공 응답이 와도 `placedOnNodeId`가 없으면 **fill이 안 바뀜**. 반환된 `imageHash`로 `use_figma`에서 직접 지정할 것.
```js
n.fills = [{type:'IMAGE', imageHash:'<반환된 hash>', scaleMode:'FILL'}]
```

**③ OG 이미지 모달 = 하단 「저장하기」 필수**
적용하기만 누르고 X로 닫으면 **리로드 시 유실**. 모달 스크롤 아래 숨은 「저장하기」까지 눌러야 영속. (OG 업로드 3단계는 [[CLAUDE.md]] 「🖼 OG 이미지 에디터 업로드」에 기록됨.)

**④ 「적용하기」 onClick은 합성 이벤트 인자 필요**
`TypeError: ... reading 'stopPropagation'` → `{stopPropagation(){},preventDefault(){},nativeEvent:{},currentTarget,target,type:'click'}` 전달.

**⑤ 에디터 프리뷰 스크린샷 = 선택 테두리(초록 점선) 박힘**
어드민용 설명 이미지는 스크린샷 ❌ → **PIL 합성** 또는 Figma 투명 export로.

---

## 미해결 / 다음 세션 진입 우선순위

1. **위 신규 함정 ①②를 [[CLAUDE.md]]·skill `cdbd-card-automation`에 정식 기록** (현재 이 문서에만 있음).
2. **사례 기획 페이지 `Google Stitch` 시안(`1079:1272`) 정리 여부** — 채택 안 된 시안에 옛 좌석 배치도("테이블 1~20") 잔존. 손대지 않음, 사용자 판단 필요.
3. (이월) 세부 질문 구성 — [[컨텍스트: 이선호/2026-07-09 유저 플로우 4구간·3문항 재개편 + 프리셋 3층 구조·10 카테고리 레시피]] 참조.
4. (이월) 분석용 에디터 인스턴스 4827~4843 삭제 여부 확인.

> 이번 세션 종결: **gala-rsvp 전 파이프라인 마감**(OG·슬러그·Figma 상세·어드민 활성화·좌석배치도 정정) + 템플릿 현황 문서 #21 등재.
