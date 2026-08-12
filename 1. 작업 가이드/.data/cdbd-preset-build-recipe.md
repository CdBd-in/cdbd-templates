# CdBd 히어로 프리셋 빌드 레시피 (editor 5541, 프리뷰 빌드) — 에이전트 자율 실행용

> 이 레시피는 CdBd 프리뷰 에디터(cdbd-client-git-ai-makevu-s-team.vercel.app/editor/5541)에서
> Figma 히어로 프리셋 1개를 **정밀 재현 + 등록**하는 검증된 절차. 질문 금지, 자율 실행.
> 브라우저는 이미 5541에 로그인·드라이버 설치된 공유 세션. **좌표 클릭 대신 fiber/JS 우선.**

## 0. 환경
```bash
cd "/Users/designer/Documents/GitHub/design/cdbd-templates"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
set -a; source .env; set +a   # CDBD_EMAIL/CDBD_PASSWORD
DRV=".claude/skills/cdbd-card-automation/card-driver.js"
```
- 시작 시 방어: `$B js "location.href"` → 5541 아니거나 /login 이면 로그인(아래) 후 `$B goto .../editor/5541; sleep 7`.
- 드라이버 설치(매 에이전트 1회): `$B eval "$DRV"` → 'installed'. `window.__cdbd` 제공.
- 로그인(필요시): goto `.../login` → `#cx_email`/`#cx_pw` id 부여 후 `$B fill` → 로그인하기 버튼 click.

## 1. 색 역할 토큰 (디폴트 테마 = 契約)
- `#fafafa`={배경색} · `#292929`={텍스트색} · `#6c4cff`={버튼색/포인트}
- 보조 텍스트 = `rgba(41,41,41,0.7)` (={텍스트색}×70%). 틴트 배경 = `rgba(41,41,41,0.06)`.
- 구분선 포인트 = `rgba(108,76,255,0.4)` (={버튼색}×40%).
- **Figma에서 뽑은 hex/opacity를 그대로 쓰되, 위 역할값과 일치**(디폴트 테마라 그대로 매핑됨).

## 2. Figma 스펙 덤프 (내 프리셋 노드 1개)
ToolSearch로 `use_figma` 로드 후 (skillNames=figma-use), 페이지 34:23 전환 후 내 노드 덤프:
```js
const page=await figma.getNodeByIdAsync("34:23"); await figma.setCurrentPageAsync(page);
function hex(c){if(!c)return null;const f=x=>('0'+Math.round(x*255).toString(16)).slice(-2);return '#'+f(c.r)+f(c.g)+f(c.b);}
function pi(ps){if(!ps||ps===figma.mixed)return null;return ps.filter(p=>p.visible!==false).map(p=>({type:p.type,color:p.type==='SOLID'?hex(p.color):null,op:p.opacity==null?1:Math.round(p.opacity*100)/100}));}
function lh(v){if(!v)return null;if(v.unit==='AUTO')return 'AUTO';return v.unit==='PERCENT'?Math.round(v.value)+'%':v.value+'px';}
function dump(n){const o={name:n.name,type:n.type,w:Math.round(n.width),h:Math.round(n.height)};
 if('layoutMode'in n){o.pad=[n.paddingTop,n.paddingRight,n.paddingBottom,n.paddingLeft];o.gap=n.itemSpacing;}
 if('fills'in n){const f=pi(n.fills);if(f&&f.length)o.fills=f;}
 if('strokes'in n&&n.strokes.length){o.strokes=pi(n.strokes);o.sw=n.strokeWeight;}
 if('cornerRadius'in n&&n.cornerRadius)o.corner=n.cornerRadius===figma.mixed?'mixed':n.cornerRadius;
 if(n.type==='TEXT'){o.align=n.textAlignHorizontal;o.segs=n.getStyledTextSegments(['fontName','fontSize','fills','lineHeight']).map(s=>({t:s.characters,size:s.fontSize,font:s.fontName.family+' '+s.fontName.style,fill:pi(s.fills),lh:lh(s.lineHeight)}));}
 if('children'in n&&n.children.length)o.children=n.children.map(dump);return o;}
return JSON.stringify(dump(await figma.getNodeByIdAsync("<NODE>")));
```
- 최상위 프레임(히어로-...) = 섹션 래퍼(카드 아님, fill #fafafa = 페이지 배경). **그 children이 각 카드**.
- children 각 프레임 = CdBd 카드 1장. 프레임 pad = 카드 내부여백[상,우,하,좌]. 프레임 fill(있으면) = 카드 배경(틴트). 그 안 TEXT/RECTANGLE/이미지프레임 = 카드 내용.
- **카드 타입 판별**: 프레임 안에 TEXT만 → 텍스트카드. `이미지`/`이미지: 로고`/`c2-main 키비주얼`/`메인 이미지` 프레임(fill #d7d7d7) → 이미지카드. `구분선`+RECTANGLE(h=1) → 구분선카드. fill #6c4cff+corner 99+흰 텍스트 pill → **pill 배지(텍스트카드 + 배경 처리, 3-7 참조)**.

## 3. 빈 페이지 확보 + 카드 구성
- **빈 활성 페이지 확보**: `boardRows()` 비어있지 않으면 → 페이지 패널 열기 → `페이지 추가` 버튼 click(맨끝 append, 새 페이지 자동 활성) → 패널 닫기.
  - 패널 열기: 좌측 `>` 토글(x<40,y120~190) fiber onClick.
  - `페이지 추가` 버튼: `[...document.querySelectorAll("button")].find(e=>e.textContent.trim()==="페이지 추가"&&e.getBoundingClientRect().width<200).click()`
  - 패널 닫기: `document.elementFromPoint(880,400).click()`
- **카드 추가** (Figma children 순서대로):
  - `window.__cdbd.openAddModal()` [sleep1.2] → `window.__cdbd.pickCardType('이미지'|'텍스트'|'구분선')` [sleep1.3]. (이 빌드는 텍스트 모달추가 정상.)
- **불필요 기본카드 삭제**: `openKebab({type})`→`menuClick('카드 삭제하기')`→`confirmSwal()` (각 sleep1~1.3). 일괄 시 매번 openKebab 재호출.
- 최종 카드 순서/개수 = Figma children과 동일해야 함.

## 4. 텍스트 카드 = Lexical setEditorState (내용·크기·볼드·줄간격) + block.style(색·여백·배경)
카드별 미리보기 contentEditable(`__lexicalEditor`)에 상태 주입 + 보드 block.style mutate.
```js
// 헬퍼(1회 설치): rowIdx=보드 인덱스, ceIdx=텍스트카드 순번(이미지/구분선 제외한 텍스트만 0based)
window.__setTC=function(rowIdx,ceIdx,o){var b=window.__cdbd.blockOfRow(window.__cdbd.boardRows()[rowIdx]);
 var ces=[...document.querySelectorAll("[contenteditable=true]")].filter(e=>e.__lexicalEditor&&e.getBoundingClientRect().x<500).sort((a,z)=>a.getBoundingClientRect().y-z.getBoundingClientRect().y);
 var ce=ces[ceIdx],ed=ce.__lexicalEditor;
 b.style.padding=o.pad; b.style.textAlign=o.align||"left"; b.style.background=o.bg||"none"; b.style.borderRadius=o.radius||"0px"; b.style.color=o.color; b.style.fontSize=o.size; b.style.lineHeight=String(o.lh); b.style.fontFamily="pretendard";
 // runs: [{t,size,color,lh,bold}] — 멀티런 지원
 var runs=o.runs||[{t:o.text,size:o.size,color:o.color,lh:o.lh,bold:o.bold}];
 var children=runs.map(r=>({detail:0,format:r.bold?1:0,mode:"normal",style:"font-size: "+r.size+"px;line-height: "+r.lh+";"+(r.color?"color: "+r.color+";":""),text:r.t,type:"text",version:1}));
 var json={root:{children:[{children:children,direction:"ltr",format:o.align||"left",indent:0,type:"custom-paragraph",version:1,textFormat:0,textStyle:"",lineHeight:String(o.lh),textAlign:o.align||"left"}],direction:"ltr",format:"",indent:0,type:"root",version:1}};
 ed.setEditorState(ed.parseEditorState(JSON.stringify(json))); return "ok";};
```
- setEditorState 하나로 렌더+커밋+autosave 됨(스타일 mutate도 함께 반영). 
- **줄바꿈**: Figma 텍스트에 `\n` 있으면 run.t에 그대로 포함(Lexical text 노드가 개행 렌더). 여러 문단이면 root.children에 문단 여러 개.
- **색/투명도**: 단색이면 block.style.color + run color 동일. 70% 보조 = `rgba(41,41,41,0.7)`.
- **중앙정렬**: o.align="center" (Figma align=CENTER인 카드).

## 5. 이미지 카드 = block.style mutate + 정렬버튼 트리거 + 역할별 라이브러리 이미지
```js
// 이미지 카드 선택
(카드행 자식 div fiber onClick). 그 후:
var b=window.__cdbd.blockOfRow(row);
b.shape = <원형이면 "circle", 각진/사각이면 "square">;
b.style.width = "<크기%>";           // = Figma 이미지프레임_w / (카드폭380 - 좌우pad합) * 100, 정수%. 예 로고48/(380-40)=14%. 큰이미지340/340=100%.
b.style.aspectRatio = <1:1이면 "1 / 1", 원본이면 "auto">;  // Figma 로고 48x48=1:1, 키비주얼 380x380=1:1(정사각), 340x340=1:1.
b.style.justifyContent = <좌측 "left"(=flex-start), 중앙 "center">;  // Figma 로고 x=좌pad → left. 중앙배치 → center.
b.style.padding = "<상>px <우>px <하>px <좌>px";  // Figma 이미지프레임 pad
b.style.borderRadius = "0px"; b.style.background="transparent";
// 트리거: 이미지 패널 정렬 버튼 클릭(좌/중), 좌표는 패널 정렬행에서 찾기
```
- 정렬 버튼 트리거: 패널의 정렬 3버튼 중 목표(좌 or 중) 좌표를 찾아 mouse이벤트 클릭 → 커밋.
- **역할별 라이브러리 이미지 적용** (빈 카드로 두지 말 것): 이미지 카드 미리보기 `이미지 업로드하기` → 라이브러리 모달 → 역할 매핑으로 선택+적용:
  - **로고 이미지**(이미지: 로고) → 라이브러리 **로고 이미지**
  - **큰/키비주얼 이미지**(메인 이미지·c2-main) → 라이브러리 **sample 이미지**
  - **프로필** → 프로필 이미지 (히어로엔 없음)
  - 방법: `window.__cdbd.openImageUpload(<이미지카드 0based순번>)` [sleep1.5] → 라이브러리 모달에서 파일명/alt 부분일치로 셀 선택 후 **적용하기**. `window.__cdbd.applyImage('<로고|sample|프로필 매칭어>')`. 모달 닫히면 성공. (라이브러리에 이미 sample/로고/프로필 이미지 존재.)
  - ⚠️ 이미지 적용 후 크기/모양/정렬이 리셋될 수 있으니 **이미지 적용 → 그 다음 block.style mutate+트리거** 순서 권장.

## 6. 구분선 카드 = block.divider mutate + 모양버튼 트리거
```js
// 구분선 카드 선택 후
var b=...; b.divider.strokeColor="rgba(108,76,255,0.4)"; b.divider.strokeWidth=<Figma RECTANGLE h, 보통1>; b.divider.shape="straight";
b.style.padding="<상>px <우>px <하>px <좌>px";  // Figma 구분선 프레임 pad (예 10 20 12 20)
// 트리거: 구분선 패널 "모양" 첫 버튼(straight) mouse이벤트 클릭
```

## 7. 틴트 배경 / pill 배지
- **틴트 카드 배경**(프레임 fill #292929 op0.06 등): 해당 카드 `b.style.background="rgba(41,41,41,0.06)"` (setEditorState/트리거로 커밋). 섹션 내 여러 카드가 같은 틴트면 전부 동일값.
- **pill 배지**(fill #6c4cff+corner99+흰 텍스트): 텍스트 카드로 처리 — `b.style.background="#6c4cff"`, `b.style.borderRadius="99px"`, run color `#fafafa`, size Figma대로, 카드 pad Figma대로. (CdBd 텍스트카드는 전폭이라 hug pill 정확재현 어려움 → 배경+둥근모서리+흰글자로 근사. 검수에서 flag되면 남겨둠.)

## 8. 프리셋 저장·등록 (검증됨: 키 인풋 직접 세팅 가능)
1. `프리셋 설정`(상단, y<80) click → 드롭다운.
2. `지금 내용을 프리셋으로 저장` 항목: `document.elementFromPoint(cx,cy)`에 pointerdown/mousedown/pointerup/mouseup/click 시퀀스(일반 click 안먹음). 모달 열림('프리셋 키' 텍스트 확인).
3. **레이아웃 스타일 토글** (미니멀/에디토리얼/볼드/공통 라벨 버튼, **다중선택**):
   - 라벨 좌표 ≈ 미니멀(582,315)·에디토리얼(663,315)·볼드(740,315). 텍스트로 재확인. **클릭 = mouse이벤트 시퀀스**(일반 click 안먹음).
   - 기본 미니멀 ON. **목표 태그(들) ON + 미니멀 OFF**. 
     - **단일 레이아웃**(에디토리얼 전용 등): 에디토리얼 ON → 미니멀 OFF. 세그먼트=editorial.
     - **공통(멀티태그)**: 해당 레이아웃 여러 개 ON(예 에+볼 = 에디토리얼 ON + 볼드 ON) → 미니멀 OFF. 세그먼트=mixed. (여러 토글 = 여러 레이아웃 공통 등록.)
4. **섹션 목적** = `히어로`.
5. **프리셋 키** — 키 인풋에 **직접 세팅 가능**(검증됨): `var ki=[...document.querySelectorAll("input")].find(e=>/^sec\//.test(e.value)); var set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value").set; set.call(ki,"<목표키>"); ki.dispatchEvent(new Event("input",{bubbles:true})); ki.dispatchEvent(new Event("change",{bubbles:true}));`
   - **목표키가 지정된 경우**(에디토리얼 전용 sec/editorial/hero/NN): 위로 직접 세팅. 상태 재계산됨(🟢새로/🔴덮어쓰기).
   - **공통(자동번호)**: 토글만 맞추고 키는 자동(sec/mixed/hero/NN). 필요시 `새로운 키 발급` 버튼으로 다음 번호. 실제 키 기록.
6. 메모(선택): "Figma <NODE> · <태그> 히어로".
7. 저장: 🟢신규면 `새 초안으로 생성`, 🔴기존키 덮어쓰기면 `변경사항 저장`(+확인 다이얼로그 '저장'). 
8. 토스트 `초안 저장됨: <키> — /admin/ai/presets` 확인. **실제 키 기록/반환.**
- ⚠️ 5546에서 만든 `sec/editorial/hero/01`(=3280:367)·`/02`(=3280:374)가 이미 존재 → 367·374는 그 키로 **덮어쓰기**(변경사항 저장). 384~는 새 번호.

## 9. 자체 검증 (저장 전)
- `boardRows()` 순회하며 각 카드 block.style(pad/color/fs/lh/bg/radius/align) + 텍스트 content run(size/bold/text) + 이미지(shape/width/ar/jc) + divider를 Figma 스펙과 **1:1 대조**. 불일치 시 수정 후 재확인.
- 스크린샷으로 시각 확인.

## 10. 자주 나는 문제
- 새 에디터/페이지에서 테마 온보딩 모달·코치마크 뜨면 닫기(5541은 기존이라 보통 없음).
- setEditorState는 해당 페이지 미리보기 CE에만 — **활성 페이지가 목표 페이지인지** 먼저 확인(boardRows 카드가 내가 만든 것인지).
- 저장 모달 스타일 토글은 **일반 .click() 안 먹음** → mouse이벤트 시퀀스.
- 페이지 이동(reorderCard)은 **페이지 패널 열린 상태**에서만 첫 sortable=페이지.

## 11. 페이지 전환 (검수·수정용) — window.__gotoPage(N)
후반 페이지 썸네일은 클립돼 좌표클릭 불가. 썸네일 onClick을 합성이벤트로 호출:
```js
// 페이지 패널 먼저 열기(좌측 '>' 토글 fiber onClick). 그 후 설치:
window.__gotoPage=function(N){
 var lbl=[...document.querySelectorAll("*")].find(e=>e.children.length===0&&e.textContent.trim()===String(N)&&e.getBoundingClientRect().width>0&&e.getBoundingClientRect().y>380);
 if(!lbl)return "no-lbl-"+N;
 var cont=lbl.parentElement; var cands=[cont,cont.querySelector("div"),cont.previousElementSibling].filter(Boolean);
 for(var n of cands){var f=window.__cdbd.fiberOf(n);var d=0;while(f&&d<6){var oc=f.memoizedProps&&f.memoizedProps.onClick;if(typeof oc==="function"&&/o\(\)/.test(oc.toString())){oc({target:document.body});return "switched-"+N;}f=f.return;d++;}}
 return "no-handler-"+N;};
window.__gotoPage(N);   // N=1-based 페이지 번호
// 그 후 패널 닫기: document.elementFromPoint(880,400).click()
// 검증: boardRows()로 활성 페이지 카드 확인(기대 개수/타입과 대조).
```
- 활성 페이지 카드 dump: `boardRows()` 순회 + `blockOfRow` → block.style/content(JSON.parse)/image/divider.
- 텍스트 run 값: `JSON.parse(b.content).root.children[*].children[*]` = {text,format(bold),style(font-size/line-height/color)}.

## 12. 최종 페이지 매핑 (5541, 빌드 후)
1=간지미니 · 2~6=미니멀5 · 7=간지에디 · **8=367(/01) 9=374(/02) 10=384(/03) 11=398(/04) 12=409(/05) 13=422(/06) 14=430(/07) 15=B_4953:143(mixed/01) 16=C_3280:443(mixed/02) 17=471(/08) 18=503(/09)** · 19=간지볼드 · **20=518(bold/01) 21=533(/02) 22=556(/03) 23=588(/04) 24=643(/05)**
