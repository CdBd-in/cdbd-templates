---
name: cdbd-card-automation
description: Use when adding, deleting, duplicating, reordering, pinning, OR renaming (label) cards, uploading images, setting page theme colors, configuring reservation date/time/capacity, setting button links, or configuring a location card's map address in the CdBd editor (cdbd.in/editor/{id}) via automation — for 4단계 템플릿 제작. Drives cards/colors/images/reservations/links through React fiber handlers (onClick·onChange·onDragEnd·onDrop·onUpdateItem) and native input setters, not mouse-coordinate clicks. Covers 카드 추가/삭제/복제/순서변경/고정(핀)/라벨변경, 이미지 업로드/적용, 페이지 색상(배경·텍스트·버튼 hex), 예약 정보 모달(날짜·시간·정원·방문체크 필수), 버튼 링크(multiCard onUpdateItem; 전화=type 'call'), 위치 카드 주소 지오코딩(검색 선택 필수), the text-card focus gotcha, the 예약 카드 credit dialog, the card-label +1-shift gotcha (one-at-a-time converger), AND the board-scroll-causes-page-drift gotcha (select cards via fiber onClick, never scroll the board).
---

# CdBd 카드 자동화 (JS, 좌표 클릭 없음)

## Overview

CdBd 에디터에서 카드 **추가·삭제·복제·순서변경·고정(핀)·이미지 업로드·페이지 색상**을 마우스 좌표 클릭 없이 자동화한다. 핵심 원리: CdBd 에디터의 카드 목록·테마는 React 상태이고, **모달/메뉴 항목의 fiber 콜백(`onClick`·`onChange`·`onDragEnd`·`onDrop`)을 JS로 직접 호출**하면 클릭한 것과 동일하게 동작한다. 좌표 클릭보다 빠르고, 가상화(스크롤)·hover 의존 UI·OS 파일 다이얼로그에 영향받지 않는다.

## When to use

- 4단계(에디터 구현)에서 카드 다수를 빠르게 쌓거나/정리할 때
- 이전 세션 잔존 카드 일괄 삭제
- 같은 카드(텍스트·버튼 등) 반복 복제

**When NOT:** 카드 디자인 슬라이더 세부값(우측 패널) — 별도 패턴(미통합). (카드 라벨 변경은 이제 지원 — 아래 "카드 라벨(이름) 변경" 참조.)

## Quick reference (검증: editor 4903)

| 작업 | 방법 | 확인 다이얼로그 |
|---|---|---|
| 추가 (이미지·버튼·프로필·갤러리·위치·구분선·SNS·메뉴·상품·유튜브·Q&A·2열) | 모달 열기 → 타입 항목 onClick | 없음 (모달 자동 닫힘=성공) |
| 추가 (**텍스트**) | 기존 텍스트 카드 **복제** (단일 '텍스트' 모달추가는 불안정) | 없음 |
| 추가 (**예약**) | 타입 항목 onClick → **크레딧 확인 다이얼로그** 1회 더 | "예약 카드 추가하기" (⚠️ 확정은 크레딧 필요) |
| **삭제** | kebab 열기 → '카드 삭제하기' → **SweetAlert 확인** | "삭제하시겠어요?" |
| **복제** | kebab 열기 → '카드 복제하기' | 없음 (예약만 DB조회로 느림) |
| **순서 변경** | dnd-kit `onDragEnd` 직접 호출 (`reorderCard(from,to)`) | 없음 |
| **고정 (핀)** | 핀 버튼 onClick → 위치 메뉴(상단/하단) / 해제는 확인창 | 해제 시 "고정 해제하기" |
| **이미지 업로드/적용** | dropzone `onDrop` 직접 호출 → 라이브러리 선택 → 적용하기 | 없음 |
| **페이지 색상** (배경·텍스트·버튼) | 색상 더보기 → 슬롯 `onChange("#hex")` 직접 호출 (swatch 클릭 ❌) | 저장 시 "페이지 테마 변경하기" |
| **예약 정보 설정** (날짜·시간·정원) | "예약 정보 관리" 모달 → 옵션 추가(JS click) + **방문 체크 종료 일시 필수** | 없음 (모달 닫힘=저장) |
| **버튼 링크** (2단카드) | 패널 fiber `onUpdateItem(itemId,{linkButton})` 직접 호출 (UI는 크래시) | 없음 |
| **카드 선택** (스크롤 없이) | board row 자식 div fiber `onClick`(`D(m.id)`) 직접 호출 — **보드 스크롤 ❌ 드리프트** | 없음 |
| **카드 라벨(이름) 변경** | row의 title 입력(상시 존재)에 native setter+`input`+`blur()` — **한 번에 하나씩 + settle + 수렴 루프** (배치는 +1 시프트) | 없음 |

## Setup

드라이버를 페이지에 1회 설치한다(에디터 URL 로드 후):

```bash
B="$HOME/.claude/skills/gstack/browse/dist/browse"   # gstack browse
DRV=".claude/skills/cdbd-card-automation/card-driver.js"
$B goto https://www.cdbd.in/editor/{id}; sleep 4
$B eval "$DRV"                       # → 'installed'  (window.__cdbd 설치)
$B js "JSON.stringify(window.__cdbd.count())"   # 마운트된 카드 수/타입 (대략치)
```

`count()`는 **화면에 마운트된 카드만** 센다(보드 가상화). 절대수 신뢰 불가 → 성공 판정은 **모달이 닫혔는지 / 스크린샷**으로 한다.

> ⚠️ **멀티페이지 필수 (2026-07-15)**: 페이지 전환 시 CdBd가 **이전 페이지의 모바일 프리뷰 DOM을 숨긴 채 유지** → `count()`(전역 `querySelectorAll` 스캔)가 **이전 페이지 카드를 계속 읽어 stale**. **멀티페이지에서 활성 페이지 카드 검증은 `count()` 금지, `boardRows()`(가운데 보드 기준) 사용**(검증: page2 전환 후 boardRows=0인데 count=이전10). 페이지 전환 = 좌측 `>` 토글로 "N 페이지" 패널 → 썸네일 `elementFromPoint(x,y).click()`(썸네일 y≈313) → **패널 바깥 클릭으로 닫아야**(예 `elementFromPoint(825,450)`) 활성 전환 완료. 전환 후 `카드 추가`는 활성 페이지로 들어감.

## Recipes

단계 사이에 모달·메뉴·다이얼로그 렌더 대기(`sleep ~1.2`)가 **필수**. async eval 금지, bash `sleep`으로 끊는다.

**카드 추가 (텍스트 제외 모든 타입):**
```bash
$B js "window.__cdbd.openAddModal()";        sleep 1.2
$B js "window.__cdbd.pickCardType('이미지')"; sleep 1.2
# 성공 = 모달이 닫힘:
$B js "[...document.querySelectorAll('div')].some(e=>e.textContent.trim()==='카드 추가하기'&&e.getBoundingClientRect().width>300)?'OPEN(실패)':'CLOSED(추가됨)'"
```

**텍스트 카드 추가 = 기존 텍스트 카드 복제** (단일 '텍스트' 모달추가는 포커스 의존이라 JS로 안 생김):
```bash
$B js "window.__cdbd.openKebab({type:'text'})"; sleep 1
$B js "window.__cdbd.menuClick('카드 복제하기')"; sleep 1.2
```

**예약 카드 추가** (크레딧 확인 1회 더):
```bash
$B js "window.__cdbd.openAddModal()";        sleep 1.2
$B js "window.__cdbd.pickCardType('예약')";   sleep 1.2   # 크레딧 확인 다이얼로그 뜸(검증됨)
$B js "window.__cdbd.confirmReservation()";  sleep 1.2   # "카드 추가하기"(MuiLoadingButton)
```
⚠️ 확인 버튼은 **DB 예약레코드 생성 네트워크 요청**을 띄우는 LoadingButton이라, **크레딧 잔액이 충분해야** 최종 추가가 완료된다. 0-크레딧 계정에선 버튼이 로딩 상태로 멈춤(다이얼로그까지는 정상 동작 검증). 취소는 `취소하기` 버튼 클릭.

**카드 삭제** (matcher: `{type:'image'}` | `{id:'...'}` | `{index:N}`):
```bash
$B js "window.__cdbd.openKebab({type:'image'})";   sleep 1
$B js "window.__cdbd.menuClick('카드 삭제하기')";   sleep 1.2
$B js "window.__cdbd.confirmSwal()";               sleep 1.2   # SweetAlert 확인
```

**카드 복제:**
```bash
$B js "window.__cdbd.openKebab({type:'button'})";  sleep 1
$B js "window.__cdbd.menuClick('카드 복제하기')";   sleep 1.2
```

**일괄 작업:** 삭제/복제 후 행이 다시 정렬되므로 **매번 openKebab을 다시** 호출한다(이전 행 참조 무효). 추가도 매번 openAddModal부터.

**카드 순서 변경** (dnd-kit `onDragEnd` 직접 호출 — 마우스/키보드 드래그 시뮬레이션은 모두 실패):
```bash
$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"   # 현재 순서 확인 (인덱스 파악)
$B js "window.__cdbd.reorderCard(8,0)"; sleep 1.2                  # 8번 카드를 0번 위치로 이동
$B js "JSON.stringify(window.__cdbd.cardOrder().map(c=>c.type))"   # 변경 확인
```
- `cardOrder()` = 보드 표시 순서 `[{id,type}]` (dnd-kit `items` prop 기준). `reorderCard(from,to)` = from 인덱스 카드를 to 위치로.
- 연속 이동 시 **매번 cardOrder()로 인덱스 재확인** (한 번 옮기면 인덱스 전부 밀림).
- 드라이버는 **첫 sortable(카드 보드)** 의 onDragEnd를 잡는다. 갤러리·메뉴 내부에도 sortable이 있으나 카드 보드가 첫 번째라 정상 동작. 풀 원리: [[1-4-1. 에디터 페이지#🥇 dnd-kit 드래그앤드롭 자동화 (2026-06-19 기록) — 카드 순서 변경]]

## 카드 라벨(이름) 변경 — title 입력 native setter (editor 4904 검증 2026-06-24)

카드 라벨 = `block.title`(보드 행에 표시되는 이름). **모든 카드 행에 title 입력(placeholder `제목을 입력하세요`)이 상시 렌더**돼 있어 **✏️ pencil 클릭조차 불필요**. 입력의 onChange가 `e=>{ s(t), l(t) }`로 `e.target.value`를 직접 읽어 커밋(`l(t)`)하므로, **native setter + `input` 이벤트 + `blur()`** 로 스크롤·좌표 없이 변경 + 자동저장.

```bash
# 헬퍼 주입 (pencil 불필요)
$B js "window.__setTitle=function(i,title){var r=window.__cdbd.boardRows();var inp=[...r[i].querySelectorAll('input')].find(e=>e.type==='text');if(!inp)return 'no-input';var set=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;set.call(inp,title);inp.dispatchEvent(new Event('input',{bubbles:true}));inp.blur();return window.__cdbd.blockOfRow(r[i]).title;};'ok'"
# 단일 변경
$B js "window.__setTitle(30,'창업반 작품 제목')"; sleep 0.7
```

⚠️ **배치(연속 set)는 +1 시프트** — 커밋 `l(t)`이 비동기(debounce)라 빠르게 연속 호출하면 앞 커밋이 다음 활성 카드에 늦게 안착해 **카드 i가 labels[i-1]을 갖게 됨**(카드 0은 빈 값). 루프 중 즉시 검증은 통과해도 settle 후 다시 읽으면 어긋남. **단일 isolated set은 항상 정확.**

✅ **해결 = 한 번에 하나씩 수렴 루프** (전체 재스캔 → 첫 불일치 1개만 수정 → settle → 반복). 44개도 ~45회로 수렴.
```bash
# 원하는 라벨 배열 + 첫 불일치 인덱스 반환기 주입
$B js "window.__want=['강사 프로필','구분선','페이지 제목', /* ...idx 순서대로... */];window.__firstBad=function(){var r=window.__cdbd.boardRows();for(var i=0;i<window.__want.length;i++){if(window.__cdbd.blockOfRow(r[i]).title!==window.__want[i])return i;}return -1;};window.__want.length"
# 수렴 루프 (bash)
for n in $(seq 1 70); do
  bad=$($B js "window.__firstBad()")
  [ "$bad" = "-1" ] && { echo "ALL CLEAN"; break; }
  $B js "window.__setTitle($bad, window.__want[$bad])" >/dev/null; sleep 0.7
done
# 검증: 리로드(goto editor; sleep 7; eval driver) 후 firstBad()===-1 확인 → 자동저장 영속
```
- 라벨링 컨벤션(목적 위주)은 [[../CLAUDE.md]] 4단계 🏷 카드 라벨 + [[1-5-1. CdBd 에디터#7. 카드 라벨 = 목적·내용 이름]]. 참고 예시: editor 4856(채용설명회) — "회사명/슬로건/여백/초대 메시지/위치 안내/출석 등록 예약" 등.
- 텍스트 카드 본문은 `block.content`(JSON **문자열**) → `JSON.parse` 후 root 재귀로 text 추출해 목적 판단. previewText는 보통 빈 값.

## 카드 고정 (핀) — 상단/하단 고정·해제

핀 버튼(드래그 핸들 옆)을 fiber `onClick`(`currentTarget` 필요)으로 호출. (editor 4903 검증)

```bash
# 고정: 핀 버튼 → 위치 메뉴 → 상단/하단 선택
$B js "window.__cdbd.openPin({type:'button'})"; sleep 1.2   # 미고정 → '상단/하단에 고정하기' 메뉴
$B js "window.__cdbd.pinTo('top')"; sleep 1.5               # 'top' | 'bottom'

# 해제: (고정 카드)핀 버튼 → SweetAlert 확인
$B js "window.__cdbd.openPin({type:'button'})"; sleep 1.2   # 고정 → '카드 고정 해제하기' 확인창
$B js "window.__cdbd.confirmSwal()"; sleep 1.5
```

- matcher = `{type}` | `{id}` | `{index}` (openKebab과 동일).
- ⚠️ **고정된 카드는 드래그 핸들이 사라져 핀이 왼쪽으로 이동** → 위치(x)로 찾으면 실패. 드라이버는 onClick 시그니처(`unpinTitle`/`K(e.currentTarget)`)로 핀 버튼을 식별.
- 고정 여부는 핸들러 소스로 알 수 없음(항상 `unpinTitle` 포함) → **`block.fixedPosition`**(`"top"`/`"bottom"`/`null`)으로 판별. `openPin`이 자동 처리(미고정→메뉴, 고정→확인창).
- 고정 카드는 페이지 상단/하단 sticky로 표시됨 (메뉴·CTA 버튼 등에 활용).

## 이미지 카드 업로드/적용 — React onDrop·onClick

CdBd 업로드는 transient `<input type=file>`(동적 생성·제거) 패턴이라 `$B upload`/Playwright `setInputFiles()` ❌, 실제 클릭은 OS 파일 다이얼로그 timeout. → **react-dropzone의 `onDrop`을 직접 호출**한다. (editor 4903, 이미지 카드 검증 — 기존 OG/썸네일만 검증이던 것을 이미지 카드까지 확정)

```bash
# 1) 파일을 base64로 window에 주입 (10MB 이하)
B64=$(base64 -i /tmp/img.png | tr -d '\n')
$B js "window.__cdbdImg='$B64'"
# 2) N번째 이미지 카드의 업로드 모달 열기 (0-based)
$B js "window.__cdbd.openImageUpload(0)"; sleep 1.5
# 3) dropzone에 onDrop으로 업로드 → 라이브러리에 추가
$B js "window.__cdbd.uploadImage('img.png')"; sleep 3
# 4) 라이브러리에서 그 이미지 선택 + 적용하기 (filename 부분일치)
$B js "window.__cdbd.applyImage('img')"; sleep 2
# 성공 = 모달 닫힘 + 카드에 이미지 표시 (자동저장)
```

- `uploadImage`는 `window.__cdbdImg`(base64)를 읽어 `File` → `new DataTransfer()` → dropzone `onDrop({…,dataTransfer})` 직접 호출. OS 다이얼로그 우회.
- `applyImage(filenameMatch)`: 라이브러리 이미지(alt/src 부분일치) 셀의 onClick으로 선택 → **같은 셀 안의** "적용하기" 클릭. ⚠️ "적용하기"는 모든 이미지 셀에 있으므로 셀 범위로 좁혀야 함.
- OG 이미지·페이지 썸네일도 같은 패턴(트리거만 다름). 풀 원리: [[1-4-1. 에디터 페이지#함정 23: 파일 업로드는 React 합성 이벤트로 onDrop 핸들러 직접 호출 (2026-06-19 기록)]]
- 이미지 **생성·준비**(Thiings·OpenAI gpt-image-1·Flow·투명 PNG export)는 [[1-5. 이미지]] — 별개 단계.

## 페이지 색상 (배경·텍스트·버튼 hex) — swatch 클릭 없이

각 색 슬롯의 React `onChange("#hex")`를 fiber로 직접 호출한다. **swatch(색 원) 클릭·SketchPicker·hex input 필드 전부 불필요, 실제 클릭 0번.** (editor 4903 검증)

슬롯 식별은 **onChange 소스 시그니처**로 한다(위치 인덱스 ❌ — 배경 행 이미지 아이콘 때문에 어긋남): 배경=`base.background` · 텍스트=`base.color` · 버튼=`theme.button.background`. 드라이버 `setThemeColor`가 이 매칭을 처리.

```bash
# 1) 페이지 테마 패널 열기 (헤더 팔레트 아이콘) → 색상 더보기
$B js "[...document.querySelectorAll('button')].filter(b=>{const r=b.getBoundingClientRect();return r.y<90&&r.x>1000&&r.x<1030})[0]?.click()"; sleep 1
$B js "window.__cdbd.openColorPicker()"; sleep 1.2

# 2) 한 색씩 설정
$B js "window.__cdbd.setThemeColor('텍스트','#F5F1E6')"; sleep 1.2
$B js "window.__cdbd.setThemeColor('버튼','#C9A227')";   sleep 1.2
$B js "window.__cdbd.setThemeColor('배경','#0B3D2E')";   sleep 1.2

# 3) 🔁 재조정 루프 (필수) — 되돌아간 슬롯만 다시 설정, 수렴까지 (보통 2패스)
for pass in 1 2 3 4; do
  $B js "window.__cdbd.themeColors().배경!=='#0B3D2E'?window.__cdbd.setThemeColor('배경','#0B3D2E'):'ok'"; sleep 1
  $B js "window.__cdbd.themeColors().텍스트!=='#F5F1E6'?window.__cdbd.setThemeColor('텍스트','#F5F1E6'):'ok'"; sleep 1
  $B js "window.__cdbd.themeColors().버튼!=='#C9A227'?window.__cdbd.setThemeColor('버튼','#C9A227'):'ok'"; sleep 1
done
$B js "JSON.stringify(window.__cdbd.themeColors())"   # 3색 모두 일치 확인

# 4) 저장
$B js "window.__cdbd.saveTheme()";          sleep 1.5   # 변경사항 저장하기
$B js "window.__cdbd.confirmThemeWarning()"; sleep 1.2   # "페이지 테마 변경하기" 경고 → 변경하기
```

**⚠️ 왜 재조정 루프인가:** 슬롯당 핸들러가 2개(행+미리보기)이고, 배경은 setter `m`·텍스트/버튼은 setter `l`로 **서로 다른 theme 복사본**을 각자 stale 상태에서 rebuild한다. 그래서 여러 색을 무조건 연속 설정하면 마지막 호출이 앞 색을 덮어쓴다. **이미 맞는 슬롯은 건드리지 말고 불일치 슬롯만** 재설정하면 2패스 내 수렴(건드리면 재충돌). 단일 색 1개만 바꿀 땐 `setThemeColor` 1회로 충분(루프 불필요).

> 구방식(fallback): onChange가 안 통하는 픽커는 [[CLAUDE.md]] "페이지 색상 — SketchPicker 실제클릭" 항목(색 원 `$B click` + hex `$B fill`). per-card 디자인 보드 색상도 동일 onChange 구조 추정(미검증).

## ⚠️ 보드 스크롤 = 페이지 드리프트 (필수, editor 4904 검증 2026-06-24)

**카드 보드를 스크롤하면 에디터가 다른 템플릿/에디터로 튕긴다**(4904 → recruit-rsvp/4856 관측). `scrollIntoView({block:'center'})`도, 보드 컨테이너 `scrollTop` 직접 설정도 **모두 드리프트 유발** + `window.__cdbd` 소실. 단순 대기(클릭·스크롤 없음)는 18초+ 안정.
- **해결: 보드를 스크롤하지 말 것.** 카드 선택은 스크롤 없이 **board row 자식 div의 fiber `onClick`(소스에 `D(m.id)` 포함)** 을 직접 호출:
  ```bash
  # 카드를 id로 선택 (보드 스크롤 없이) — 우측 패널이 해당 카드로 갱신됨
  $B js "(function(){var r=window.__cdbd.boardRows();var el=null;for(var i=0;i<r.length;i++){var b=window.__cdbd.blockOfRow(r[i]);if(b&&b.id&&b.id.indexOf('<id8>')===0){el=r[i];break;}}if(!el)return 'nf';var all=el.querySelectorAll('div');for(var j=0;j<all.length;j++){var f=window.__cdbd.fiberOf(all[j]);if(f&&f.memoizedProps&&typeof f.memoizedProps.onClick==='function'&&/D\\(m\\.id\\)/.test(f.memoizedProps.onClick.toString())){f.memoizedProps.onClick();return 'sel';}}return 'handler-nf';})()"
  ```
- **`$B viewport` 금지** — context 재생성("refs/load-html replayed")이 이전 네비게이션을 replay해 4856으로 드리프트. 작업 시작 시 1회만 설정하고 이후 건드리지 말 것.
- 드리프트/크래시(about:blank) 복구: `$B goto editor/{id}; sleep 7` → 로그인 풀렸으면 재로그인 → `$B eval card-driver.js` 재설치.

## 예약 정보 설정 — 모달 (editor 4904 검증 2026-06-24)

예약 **카드 추가**(위 Recipes)와 별개로, 실제 날짜·시간·정원은 **우측 패널 "예약 정보 관리" 모달**에서 설정한다. `block.reservation`은 서버측이라 직접 mutation 불가.

**🔑 핵심 함정 — 방문 체크 가능 시간(종료 일시)이 필수.** 안 채우면 "변경사항 저장하기"가 빨간 에러("종료 날짜/시간을 선택해 주세요.")로 막혀 모달이 안 닫힘. (이전 세션 예약 저장 유실의 진짜 원인.) **시작 일시는 첫 옵션 날짜로 자동 채워지고, 종료 일시만 수동 입력** 필요.

**⚡ 속도 (editor 4904 실측 2026-06-24): 옵션 1개 추가 ≈ 5.0초**(아래 단축 sleep). 예약 카드 1개(옵션 2개 + 방문체크 종료) ≈ 15~18초, 3개 ≈ 45~55초. 기존(넉넉한 sleep)대비 **~40% 단축**, 신뢰성 유지.

레시피 (한 예약 카드):
```bash
# 1) 카드 선택 (위 fiber onClick 방식, 보드 스크롤 ❌) → "예약 정보 관리" 버튼의 fiber onClick은 ()=>P(!0)
#    ⚠️ 관리 버튼은 $B click이 자주 타임아웃(actionable 대기) → JS로 onClick 직접 호출이 빠르고 안정.
$B js "(function(){var d=[...document.querySelectorAll('*')].filter(e=>e.textContent.trim()==='예약 정보 관리'&&e.children.length<=2&&e.getBoundingClientRect().x<1000)[0];var node=d;var depth=0;while(node&&depth<6){var f=window.__cdbd.fiberOf(node);var fd=0;while(f&&fd<6){if(f.memoizedProps&&typeof f.memoizedProps.onClick==='function'){f.memoizedProps.onClick();return 'opened';}f=f.return;fd++;}node=node.parentElement;depth++;}return 'nf';})()"; sleep 1

# 2) 기본정보 ($B fill 정상 작동 — 제목 포함)
#    제목=placeholder '제목을 입력해 주세요.' / 장소='주소 혹은 장소명을 입력해 주세요.' / 호스트='호스트 이름을 입력해 주세요.' / 연락처='호스트 연락처를 입력해 주세요.'
$B fill "#res-title" "심화반 수강 신청"   # 각 input에 id 부여 후 $B fill

# 3) 예약 옵션 추가 (반복) — 모달 내부는 JS .click()만! ($B click은 about:blank 크래시) · sleep 단축
$B js "[...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='옵션 추가').click()"; sleep 0.6
#   날짜: 날짜 input의 형제 button(캘린더 아이콘) JS .click() → MuiPickersDay 중 텍스트=일자 클릭 (캘린더 기본=현재월, 다른 달이면 next/prev 화살표 필요)
$B js "(function(){var di=[...document.querySelectorAll('input')].find(e=>e.placeholder==='날짜를 선택해 주세요');var w=di.closest('.MuiTextField-root')||di.parentElement.parentElement;w.querySelector('button').click();})()"; sleep 0.5
$B js "[...document.querySelectorAll('button.MuiPickersDay-root')].filter(b=>b.textContent.trim()==='25'&&!b.disabled)[0].click()"; sleep 0.3
#   시간: 시간 input의 형제 button → [role=option] aria-label '19 hours' / '0 minutes' 연속 클릭 (팝업 열린 후 리스트 즉시 렌더)
$B js "(function(){var ti=[...document.querySelectorAll('input')].find(e=>e.placeholder==='시간을 선택해 주세요');var w=ti.closest('.MuiTextField-root')||ti.parentElement.parentElement;w.querySelector('button').click();})()"; sleep 0.5
$B js "(function(){var o=[...document.querySelectorAll('[role=option]')].find(e=>e.getAttribute('aria-label')==='19 hours');o.scrollIntoView({block:'center'});o.click();})()"; sleep 0.25
$B js "(function(){var o=[...document.querySelectorAll('[role=option]')].find(e=>e.getAttribute('aria-label')==='0 minutes');o.scrollIntoView({block:'center'});o.click();})()"; sleep 0.25
$B fill "#res-count" "5"                     # 인원 input(placeholder '인원을 입력해 주세요'); sleep 0.2
$B js "[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='설정하기').click()"; sleep 0.7

# 4) 방문 체크 가능 시간 — 종료 일시 필수! (시작은 자동) — placeholder '날짜'/'시간', value==='' 인 것이 종료
$B js "(function(){var end=[...document.querySelectorAll('input')].filter(e=>e.placeholder==='날짜').find(e=>e.value==='');var w=end.closest('.MuiTextField-root')||end.parentElement.parentElement;w.querySelector('button').click();})()"; sleep 0.5
$B js "[...document.querySelectorAll('button.MuiPickersDay-root')].filter(b=>b.textContent.trim()==='27'&&!b.disabled)[0].click()"; sleep 0.3
$B js "(function(){var end=[...document.querySelectorAll('input')].filter(e=>e.placeholder==='시간').find(e=>e.value==='');var w=end.closest('.MuiTextField-root')||end.parentElement.parentElement;w.querySelector('button').click();})()"; sleep 0.5
$B js "(function(){var o=[...document.querySelectorAll('[role=option]')].find(e=>e.getAttribute('aria-label')==='18 hours');o.scrollIntoView({block:'center'});o.click();})()"; sleep 0.25
$B js "(function(){var o=[...document.querySelectorAll('[role=option]')].find(e=>e.getAttribute('aria-label')==='0 minutes');o.scrollIntoView({block:'center'});o.click();})()"; sleep 0.25

# 5) 저장 — "변경사항 저장하기"도 fiber onClick으로(또는 $B click). 모달이 닫히면 성공(서버 저장). 종료 일시 누락이면 빨간 에러로 안 닫힘.
$B js "[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='변경사항 저장하기').click()"; sleep 2.5
$B js "![...document.querySelectorAll('input')].find(e=>e.placeholder==='제목을 입력해 주세요.')?'SAVED(모달닫힘)':'OPEN(에러확인)'"
```
- **검증/식별**: 저장 성공 시 우측 패널 "예약 정보"에 제목 표시 + 프리뷰 placeholder("오른쪽에서 예약 정보를…")가 **"예약하기" 버튼**으로 바뀜. 빈 카드 판별 = 모달 열어 제목 input value==='' 확인.
- 여러 예약 카드는 **매번 fiber onClick으로 정확히 선택**(라벨/위치로 추정 ❌ — 같은 'reservation' 타입이라 헷갈림).
- **모달 취소(저장 폐기)**: 스테이징된 변경이 있으면 "저장 없이 나가기" 확인 다이얼로그 → **"나가기"** 클릭. (테스트로 임시 옵션 추가 후 서버 데이터 보존하며 빠져나올 때 유용.)

### ⚡ 날짜·시간 픽커 = dayjs onChange 직접 주입 (2026-07-07 5025 검증 — 캘린더/리스트 클릭 0번, S6 ~50-60%↓)

**해결됨** — 구 2026-06-24 "불가/비추천" 판정 뒤집힘. MUI X 날짜·시간 픽커에 앱 onChange로 dayjs를 주입하면 팝업 없이 즉시 세팅되고 **요일 `(토)`도 자동 파생**(타이핑 방식이 못 풀던 weekday 문제 해결).

1. **dayjs 어댑터 추출** (모달당 1회) — `window.dayjs`는 없지만 MUI `LocalizationProvider` **context**에 AdapterDayjs가 있음. 날짜 input fiber를 타고 올라가며 context dependency 중 `.date()` 함수 보유 객체(`lib:'dayjs'`)를 찾음:
   ```js
   var di=[...document.querySelectorAll('input')].find(e=>e.placeholder==='날짜를 선택해 주세요');
   var f=window.__cdbd.fiberOf(di),adapter=null,d=0;
   while(f&&d<25){var dep=f.dependencies&&f.dependencies.firstContext;while(dep){var v=dep.memoizedValue;if(v){var c=v.utils||v;if(typeof c.date==='function')adapter=c;}dep=dep.next;}if(adapter)break;f=f.return;d++;}
   ```
2. **날짜·시간 세팅** — 각 input fiber 체인에서 onChange 중 **소스에 `isValid()` 포함**한 앱 핸들러를 찾아 dayjs 주입. ⚠️ depth로 고정 ❌(depth~13은 MUI 내부 field onChange라 무효) → 앱 핸들러는 `e=>{if(e&&e.isValid()){...er({...en,date/time...})}}`:
   ```js
   function inject(ph,iso){var i=[...document.querySelectorAll('input')].find(e=>e.placeholder===ph);var f=window.__cdbd.fiberOf(i),fn=null,g=0;while(f&&g<25){var p=f.memoizedProps;if(p&&typeof p.onChange==='function'&&/isValid\(\)/.test(p.onChange.toString())){fn=p.onChange;break;}f=f.return;g++;}return fn(adapter.date(iso));}
   inject('날짜를 선택해 주세요','2026-10-17T00:00:00');   // → 필드 "2026.10.17(토)"
   inject('시간을 선택해 주세요','2026-10-17T19:30:00');   // → 필드 "19:30"
   ```
   방문체크 종료 일시도 동일(단 placeholder '날짜'/'시간' 중 `value===''`인 종료 필드 타게팅).
3. 인원 `$B fill` + `설정하기`는 기존대로.
- **효과**: 옵션당 픽커 클릭(캘린더 open+day + 시간 open+hour+minute ~2초) → onChange 2회(~0.2초). **옵션당 ~5초→~2초, S6 전체 ~50-60% 단축.** (구 결론의 "옵션당 ~5초 하한"은 픽커 클릭 전제라 무효화.)
- ⚠️ input 식별 = placeholder / onChange 식별 = **소스 `isValid()`**(depth 아님). 어댑터·핸들러 모두 모달 열릴 때마다 재탐색(fiber 재생성).

## 버튼 링크 — 2단카드(multiCard) `onUpdateItem` (editor 4904 검증 2026-06-24)

2단카드 버튼/이미지 등의 **링크 연결**은 UI(레이아웃 탭 구성 버튼 행 클릭)가 **about:blank 크래시**를 유발하고, 디자인 탭 URL input은 `$B fill`·로컬 `Y(value)` onChange 모두 **블록 미반영**. → 패널 fiber의 **`onUpdateItem(itemId, {linkButton})`** 직접 호출(자동저장까지 반영).

```bash
# 2단카드 선택(fiber onClick) 후, 패널 fiber에서 onUpdateItem 회수해 각 item 링크 설정
$B js "(function(){
  var u=[...document.querySelectorAll('input')].find(e=>e.placeholder==='URL을 입력해주세요');  // 디자인 탭이 열려 있어야 함
  var f=window.__cdbd.fiberOf(u);var d=0;var oui=null;
  while(f&&d<25){if(f.memoizedProps&&typeof f.memoizedProps.onUpdateItem==='function'){oui=f.memoizedProps.onUpdateItem;break;}f=f.return;d++;}
  var r=window.__cdbd.boardRows();var blk=null;
  for(var i=0;i<r.length;i++){var b=window.__cdbd.blockOfRow(r[i]);if(b&&b.id&&b.id.indexOf('<multiCard-id8>')===0){blk=b;break;}}
  var items=blk.multiCard.items;  // items[].content 의 Lexical text로 어느 버튼인지 식별
  oui(items[0].id,{linkButton:{link:{href:'tel:010-2345-6789',openNewTab:false},text:'버튼',type:'call'}});   // 전화: type 'call'(전화하기) — UI 필드엔 번호만, href는 tel: 유지
  oui(items[1].id,{linkButton:{link:{href:'https://pf.kakao.com/_xxxx',openNewTab:true},text:'버튼',type:'url'}}); // 외부링크
  return 'done';
})()"
# 검증: 리로드(goto editor; sleep 7; eval driver) 후 blockOfRow(...).multiCard.items[].linkButton.type/.link.href 확인 → 자동저장 영속
```
- `onUpdateItem` 소스 = `(e,t)=>{ J({...Y, items: q.map(l=> l.id!==e? l : {...l,...t}) }) }` — 특정 item만 patch, J가 블록 commit.
- **🔑 전화 버튼 = `type:'call'`(전화하기), `type:'url'`+`tel:` 아님** (editor 4904 검증 2026-06-24). 디자인 탭 "링크 연결" 드롭다운을 **"전화하기"** 로 바꾸고 필드엔 **번호만**(`010-2345-6789`) 입력 → 내부 href는 `tel:번호` 유지·type `call`. (UI 드롭다운: `URL 열기` 버튼 클릭 → 메뉴 버튼 중 "전화하기" `.click()` → 필드 `$B fill` 번호. 또는 위 onUpdateItem로 `type:'call'` 직접 지정.)
- **linkButton.type 6종**: `url`(URL 열기, http·tel·임의) / `call`(전화하기, 번호) / `message`(문자 보내기) / `email`(이메일 보내기) / `kakao`(카카오톡 공유하기) / `contact`(연락처 저장하기). 드롭다운 라벨↔type 매칭은 위 6개 순서.
- **위치(location) 카드 "지도로 이동" 버튼 = 빌트인**, 단 **주소를 검색 드롭다운에서 선택(지오코딩)해야 동작** (아래 "위치 카드 주소" 참조).

## 위치 카드 주소 — 검색 선택(지오코딩) 필수 (editor 4904 검증 2026-06-24)

위치 안내 카드의 "지도 보기" 버튼은 `block.location`에 **`lat`·`lng`·`naverMapsUrl`이 있어야 이동**한다. 주소를 **직접 타이핑만 하면**(`address`/`inputValue`만 채워짐) 좌표가 없어 **버튼이 동작 안 함**(흔한 "지도 안 열림" 원인). **반드시 주소 검색 드롭다운에서 결과를 클릭해 선택** → 그 순간 `lat`/`lng`/`naverMapsUrl` 생성 + 자동저장.

```bash
# 위치 카드 선택(fiber onClick) 후 주소 입력 포커스 → 드롭다운 후보 클릭
$B js "(function(){var el=[...document.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().x>940&&e.textContent.trim()==='<지오코딩 후보 주소 정확일치>'&&e.children.length<=1)[0];if(!el)return 'nf';var r=el.getBoundingClientRect();document.elementFromPoint(r.x+r.width/2,r.y+r.height/2).click();return 'sel';})()"; sleep 2
$B js "var l=window.__cdbd.blockOfRow(window.__cdbd.boardRows()[<idx>]).location;JSON.stringify({lat:l.lat,lng:l.lng,hasUrl:!!l.naverMapsUrl,button:l.button})"
```
- ⚠️ 선택 시 표시 주소가 **지오코더 POI명**으로 바뀜(예: "와우산로 94" → "…와우산로 94 학교법인홍익학원"). 텍스트를 다시 손으로 고치면 좌표가 또 날아감 → 라벨 바꾸려면 **검색해서 다른 결과 선택**으로.
- `button:true`(지도 보기 버튼 표시) + `label:true`(주소 표시)는 카드 구성 토글. 지도 버튼은 **위치 카드 빌트인 컴포넌트**(별도 버튼 카드 ❌).

## OG 썸네일 — 자동화 불가 (수동, editor 4904 확인 2026-06-24)

헤더 🌐 globe("URL 정보 편집하기") 모달의 **제목·설명은 `$B fill`/onChange로 설정 가능**하나, **썸네일(800×400)은 자동화 불가**. 썸네일 img는 cursor:auto·onClick 없음·dropzone/onDrop 없음·호버 오버레이 없음 = **transient OS 파일 다이얼로그**만 존재. 카드 이미지의 onDrop 패턴이 OG 썸네일엔 없음. → **사용자 수동 업로드**(800×400 이미지 준비해 전달). 제목/설명은 자동, 썸네일만 수동.

## Common mistakes

| 증상 | 원인·해결 |
|---|---|
| `pickCardType` 했는데 모달 안 닫힘 | 잘못된 래퍼 onClick을 잡음. 드라이버는 **항목 컴포넌트(Icon/title/description prop 보유)** 의 onClick만 매칭해 회피 — 모달이 완전히 렌더된 뒤(>1s) 호출했는지 확인 |
| 단일 '텍스트' 추가가 안 됨 | 정상. 텍스트는 포커스(selected_block_id) 의존 → **복제**로 추가 |
| `count()`가 안 변함 | 가상화로 새 카드가 화면 밖 미마운트. 정상. 스크린샷/모달닫힘으로 판정 |
| `openKebab` "no-kebab-button" | kebab은 hover시 보이지만 DOM엔 존재. 행 매칭 실패가 흔함 → matcher 타입/인덱스 확인. 보드 행 필터는 `x>540 && width>280 && 40<h<90` |
| 예약 카드만 누락 | `confirmReservation()` 안 부름(확인 1회 더). 또는 크레딧 부족으로 LoadingButton 멈춤 — 크레딧 있는 계정에서 실행 |
| 삭제했는데 안 지워짐 | `confirmSwal()` 누락. 삭제는 항상 SweetAlert 확인 필요 |
| 페이지가 대시보드로 튕김 | 모달 X버튼 셀렉터 오타로 다른 요소 클릭됨. 모달 닫기는 추가 성공 시 자동(`i(!1)`). 강제로 닫지 말 것 |

## 내부 동작 (참고)

- 추가: 타입 항목 onClick = `()=>{ t({id:uuid(), type:"image", style:{...theme}, ...}), i(!1) }` — `t`=블록 append setter, `i(!1)`=모달 닫기. setter `t`는 클로저라 단독 추출 불가 → 항목 onClick 호출이 유일 경로.
- 삭제: `async()=>{ if(!(await confirm(...)).isConfirmed)return; ...blocks.filter(b=>b.id!==m.id)... }`
- 복제: `async()=>{ let id=uuid(), clone=rK.X2(m); append({...clone,id}); }` — 예약은 Supabase 조회 추가.
- 식별은 **라벨 아님, fiber `block.type`** ([[CLAUDE.md]] SVG 시그니처 원칙과 동일 취지: DOM 텍스트로 추정 금지).

전체 드라이버: `card-driver.js` (window.__cdbd 메서드: openAddModal, pickCardType, confirmReservation, openKebab, menuClick, confirmSwal, count, blocks, blockOfRow).
