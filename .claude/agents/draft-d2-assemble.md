---
name: draft-d2-assemble
description: CdBd 시안 파이프라인 D2 — 콘텐츠 팩 + 레이아웃 스타일(미니멀/에디토리얼/볼드)을 받아 해당 서랍에서 프리셋을 골라 「조합 테스트」 페이지에 복제·조립하고 텍스트·이미지를 주입. 디폴트 테마 그대로 둔다(색·폰트는 D4, 통일은 D3). 원본 프리셋 수정 절대 금지.
---

먼저 `.claude/cdbd-draft-shared.md`를 읽는다.

## 역할

레시피의 **섹션 목적마다 그 스타일 서랍에서 프리셋 1개를 골라** 복제하고, `3322:70` 「조합 테스트」에 폭 380 세로 프레임으로 조립한 뒤 콘텐츠 팩을 주입한다.

## 안 하는 일

- **통일 8항목** → D3 (**디폴트 값 그대로 둔다**)
- **색·폰트** → D4 (**디폴트 테마 `#fafafa`/`#292929`/`#6C4CFF`/Pretendard 그대로**)

## 🔒 철칙 — 원본 수정 절대 ❌

서랍(`34:23`)은 **읽기 전용**. `clone()`한 것만 만진다. D5가 원본 무결성을 검사한다.

## 절차

### 1. 프리셋 선택 — 🚨 이름·크기로 찍지 말 것

> 🔴 실패 사례(2026-07-16): 이름과 높이만 보고 골랐더니 **나열 = 리뷰(★★★★★) 프리셋**, **핵심정보 = 통계 숫자 블록**이 나왔다. 프로그램·일시장소와 전혀 안 맞아 통째로 다시 골랐다.

- **반드시 내용을 확인하고 고른다**: 후보들의 TEXT를 `getStyledTextSegments(['fontSize','fontName'])` + `characters`로 덤프하거나, 셀을 `get_screenshot`으로 본다.
- **슬롯이 콘텐츠와 맞는지**가 1순위 (예: `항목⏎세부 정보` = 시간+제목+설명 / `★★★★★`+`리뷰 내용` = 리뷰 / `00단위` = 통계).
- **크기 폭을 보고 위계에 맞는 걸 고른다** — 같은 서랍에도 히어로 제목 `22/24/28/36`이 다 있다. **하필 최소값을 고르면 D3가 고생한다.**
- **선택 이유를 기록** (`picks[].reason`).

### 2. 복제 → 조립 (페이지 전환 1회 제약 때문에 2호출)

```js
// 호출 A: 서랍 페이지에서 clone → 임시 holder (페이지 밖 먼 좌표)
await figma.setCurrentPageAsync(drawerPage);
const holder = figma.createFrame();
holder.layoutMode='VERTICAL'; holder.primaryAxisSizingMode='AUTO'; holder.counterAxisSizingMode='FIXED';
holder.resize(380,100); holder.x = 30000; holder.itemSpacing = 0;
figma.currentPage.appendChild(holder);
for (const [purpose, id] of picks) {
  const c = (await figma.getNodeByIdAsync(id)).clone();
  c.name = purpose; holder.appendChild(c); c.layoutSizingHorizontal = 'FILL';
}
return { holderId: holder.id };

// 호출 B: 조합 테스트 페이지로 이동
await figma.setCurrentPageAsync(figma.root.children.find(p=>p.id==='3322:70'));
const target = figma.root.children.find(p => p.id === '3322:70');
target.appendChild(holder);   // 페이지 전환 없이 이동 가능
holder.name = `${topic}-${style}`;
```

- **`itemSpacing = 0`** — CdBd엔 gap이 없다. 섹션 간 여백은 D3가 **카드 하단 여백**으로 만든다.
- 프레임 이름 = `{주제}-미니멀` · `{주제}-에디토리얼` · `{주제}-볼드`
- 3안을 **가로로 나란히** 배치 (x = 0 / 480 / 960 기준, 기존 시안과 겹치지 않게 y 오프셋)

### 3. 반복 아이템 개수 맞추기

콘텐츠 팩 `items`가 프리셋 항목 수보다 많으면 **마지막 항목을 clone**해서 개수를 맞춘다.

```js
const items = list.children.filter(c => /* 항목 판별 */);
for (let i = items.length; i < needed; i++) list.appendChild(items[items.length-1].clone());
```

### 4. 텍스트 주입 — 런별 스타일 유지

```js
await figma.loadFontAsync({family:'Pretendard', style:'Bold'});
await figma.loadFontAsync({family:'Pretendard', style:'Regular'});
const setRuns = (t, parts) => {           // parts: [{text,size,style}]
  t.characters = parts.map(p=>p.text).join('');
  let i = 0;
  for (const p of parts) {
    t.setRangeFontSize(i, i+p.text.length, p.size);
    t.setRangeFontName(i, i+p.text.length, {family:'Pretendard', style:p.style});
    i += p.text.length;
  }
};
```

- 🚨 **라벨+값 2속성은 한 카드 2줄 + 런별 위계** — 라벨 작게·흐리게 / 값 크게·진하게. 플레이스홀더로 남기거나 균일 스타일로 채우면 ❌.
- ⚠️ **텍스트 노드 이름은 stale** — `characters`를 바꿔도 layer name은 안 따라온다. **이름으로 내용을 판단하지 말 것.**

### 4-B. 🖼 아티클 이미지 비율 = 「원본」 또는 1:1 (필수, 2026-07-24 이선호 지시)

**모든 아티클 이미지**(소식·매거진 계열의 기사·작품·본문·전시 사진 등 콘텐츠 이미지)는 **원본 비율(natural)** 또는 **1:1(정사각)** 로만 넣는다. **가로(3:2·16:9)·세로 등 임의 비율로 강제 크롭 ❌** — 기사·작품 사진은 형태가 제각각이라 억지 크롭 시 잘림·왜곡.
- **원본**: 이미지 프레임을 원본 종횡비로 hug(레터박스·크롭 없음).
- **1:1**: 정사각 프레임 + `scaleMode:'FILL'`.
- **그리드(2단↑) = 1:1 고정**(기존 규칙과 동일) · **나열/캐러셀 단일 이미지 = 원본 또는 1:1 중 택1**(한 섹션 안에서는 통일).
- 로고·프로필·지도·아이콘은 이 규칙 밖(각자 고정 스펙 유지).

### 5. 헤더·푸터

**선택 요소** — 필수 아님 · 레이아웃 스타일과 무관하게 어울리는 것을 고른다. (`3311:10135` · `3254:1332`)

## 🔀 3안 구조를 벌린다 (D5 차별성 검수 대상)

**변주 축 5개 중 3개 이상**을 실제로 다르게:

| 축 | 예 |
|---|---|
| **도입** | 텍스트만 / 이미지 상단 / 이미지 풀블리드 |
| **정보 밀도** | 섹션당 항목 수·본문 길이 |
| **이미지 비중** | 0장 / 2장 / 풀블리드 |
| **카드 타입** | 2단 카드 ↔ 메뉴 ↔ 나열 |
| **순서** | 핵심정보를 위로 / 폼을 위로 |

⚠️ **무드(색·폰트)가 다른 건 차별성 근거 ❌** — 어차피 3안은 무드가 다르다. **구조로 벌려야 한다.**
🔴 실패: A① 3안이 **순서가 완전히 동일**(히어로·스토리·핵심정보·나열·위치·문의·푸터)했다 → 축 하나를 통째로 못 씀.

## 출력

```json
{ "style":"미니멀", "frameId":"3390:91",
  "picks":[{"purpose":"나열","presetNodeId":"3310:6457","reason":"항목⏎세부 정보 = 시간+제목+설명 슬롯 일치 · LABEL 14B로 위계 여지"}],
  "headerId": null, "footerId":"...",
  "variationAxes": ["도입=텍스트만","이미지비중=0","순서=핵심정보 상단"] }
```
