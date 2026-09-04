// ═══ 6-① ~ 6-④ 조립 재개 스크립트 (2026-09-04) ═══
// 상태: 6-①(3안) · 6-②(3안) 완료 / 6-③(3안) · 6-④(3안) 미완료
//   → Figma 파일이 read-only 모드로 전환되어 중단됨
//     ("Cannot create node with type FRAME" / "Cannot write to node property in a read-only file or mode")
//     Figma 데스크톱 앱을 Dev Mode → Design Mode 로 되돌리거나 편집 권한 회복 후 재개할 것.
//
// 완료된 프레임 node ID
//   6-①-미니멀      5920:583
//   6-①-에디토리얼  5920:1226
//   6-①-볼드        5920:2413
//   6-②-미니멀      5920:4031
//   6-②-에디토리얼  5920:5601
//   6-②-볼드        5920:6567
//
// 아래 PRELUDE 를 use_figma 코드 맨 앞에 붙이고, 각 BUILD 블록을 이어 붙여 실행한다.
// fileKey 24O01lprp5i2ufl7CbZXXx · 대상 페이지 5843:37 · setCurrentPageAsync 호출 금지.

// ─────────────────────────── PRELUDE ───────────────────────────
const PRELUDE = String.raw`
const h2r=h=>{h=h.replace("#","");return{r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};};
const r2h=c=>"#"+[c.r,c.g,c.b].map(v=>Math.round(v*255).toString(16).padStart(2,"0")).join("");
let STYLES=null;
async function initFonts(){if(STYLES)return;STYLES={};(await figma.listAvailableFontsAsync()).forEach(f=>{(STYLES[f.fontName.family]=STYLES[f.fontName.family]||[]).push(f.fontName.style);});}
const RANK=["Thin","ExtraLight","Light","3 Light","DemiLight","Regular","4 Regular","Medium","5 Medium","SemiBold","6 Bold","Bold","ExtraBold","7 ExtraBold","Black"];
function pickStyle(fam,want){const a=STYLES[fam]||[];if(!a.length)return null;if(a.includes(want))return want;const wi=RANK.indexOf(want);if(wi<0)return a[0];let b=a[0],bd=99;for(const s of a){const i=RANK.indexOf(s);if(i<0)continue;const d=Math.abs(i-wi);if(d<bd){bd=d;b=s;}}return b;}
async function setFont(fam,want){const st=pickStyle(fam,want);if(!st)return null;const fn={family:fam,style:st};await figma.loadFontAsync(fn);return fn;}
function mapArr(arr,T,dark,isStroke){return arr.map(p=>{if(p.type!=="SOLID")return p;const to=T[r2h(p.color)];let o=p.opacity===undefined?1:p.opacity;if(dark&&o<1)o=Math.min(1,o+(isStroke?0.10:0.02));if(!to)return {...p,opacity:o};return {...p,color:h2r(to),opacity:o};});}
function applyTokens(n,T,dark){
 if("fills" in n&&Array.isArray(n.fills))n.fills=mapArr(n.fills,T,dark,false);
 if("strokes" in n&&Array.isArray(n.strokes))n.strokes=mapArr(n.strokes,T,dark,true);
 if(n.type==="TEXT"&&!Array.isArray(n.fills)){for(const s of n.getStyledTextSegments(["fills"]))n.setRangeFills(s.start,s.end,mapArr(s.fills,T,dark,false));}
 if(n.children)n.children.forEach(c=>applyTokens(c,T,dark));}
function texts(n){const o=[];const w=x=>{if(x.type==="TEXT")o.push(x);if(x.children)x.children.forEach(w);};w(n);return o;}
async function remapFonts(n,TITLE,BODY,tmin){for(const t of texts(n)){for(const s of t.getStyledTextSegments(["fontName","fontSize"])){await figma.loadFontAsync(s.fontName);if(/^[—–―·•\s]+$/.test(t.characters.slice(s.start,s.end)))continue;const fam=(s.fontSize>=tmin||/Bold|Black|ExtraBold/.test(s.fontName.style))?TITLE:BODY;const fn=await setFont(fam,s.fontName.style);if(fn)t.setRangeFontName(s.start,s.end,fn);}}}
// 혼합 스타일 텍스트는 줄 단위로 원본 스타일을 복원하며 주입한다
async function injOne(t,val){
 const segs=t.getStyledTextSegments(["fontSize","fontName","fills","lineHeight"]);
 for(const s of segs)await figma.loadFontAsync(s.fontName);
 if(segs.length<=1){t.characters=String(val);return;}
 const orig=t.characters.split("\n");const styleOf=[];let pos=0;
 for(let i=0;i<orig.length;i++){let s=segs.find(g=>g.start<=pos&&g.end>pos)||segs[segs.length-1];styleOf.push(s);pos+=orig[i].length+1;}
 const lines=String(val).split("\n");t.characters=lines.join("\n");let p=0;
 for(let i=0;i<lines.length;i++){const st=styleOf[Math.min(i,styleOf.length-1)];const a=p,b=p+lines[i].length;
  if(b>a){t.setRangeFontName(a,b,st.fontName);t.setRangeFontSize(a,b,st.fontSize);t.setRangeFills(a,b,st.fills);if(st.lineHeight)t.setRangeLineHeight(a,b,st.lineHeight);}p=b+1;}}
async function inject(node,arr){const ts=texts(node);for(let i=0;i<ts.length&&i<arr.length;i++){if(arr[i]==null)continue;await injOne(ts[i],arr[i]);}return ts.length;}
function repU(sec,from,unitLen,have,want){
 const k0=sec.children.slice();
 const gapPb=k0[from+unitLen-1].paddingBottom,endPb=k0[from+unitLen*have-1].paddingBottom;
 if(want>have){let at=from+unitLen*have;for(let i=have;i<want;i++)for(let j=0;j<unitLen;j++){const c=k0[from+j].clone();sec.insertChild(at++,c);try{c.layoutSizingHorizontal="FILL";}catch(e){}}}
 else{for(let i=have-1;i>=want;i--)for(let j=unitLen-1;j>=0;j--)sec.children[from+i*unitLen+j].remove();}
 for(let i=0;i<want;i++){const l=sec.children[from+i*unitLen+unitLen-1];if("paddingBottom" in l)l.paddingBottom=(i===want-1)?endPb:gapPb;}}
function unify(root,radius,side,btnR){
 const pills=[];const w=n=>{if("cornerRadius" in n&&typeof n.cornerRadius==="number"){if(n.cornerRadius>=20)pills.push(n);else{try{n.cornerRadius=radius;}catch(e){}}}if(n.children)n.children.forEach(w);};
 root.children.forEach(w);
 for(const sec of root.children)for(const card of (sec.children||[])){
  if(!("paddingLeft" in card))continue;
  const isImg=/이미지|갤러리|지도|위치|비주얼/.test(card.name);
  if(card.paddingLeft>0||!isImg){card.paddingLeft=side;card.paddingRight=side;}}
 for(const p of pills){try{p.cornerRadius=btnR;}catch(e){}}
 return pills.length;}
function b36(sec){const k=sec.children;if(!k||!k.length)return;const l=k[k.length-1];if("paddingBottom" in l)l.paddingBottom=36;}
function alignAll(n,a){for(const t of texts(n))t.textAlignHorizontal=a;}
async function put(frame,id){const p=await figma.getNodeByIdAsync(id);const c=p.clone();frame.appendChild(c);try{c.layoutSizingHorizontal="FILL";}catch(e){}return c;}
async function newDraft(name,x){
 const page=await figma.getNodeByIdAsync("5843:37");
 const f=figma.createFrame();f.name=name;f.resize(380,100);f.layoutMode="VERTICAL";
 f.primaryAxisSizingMode="AUTO";f.counterAxisSizingMode="FIXED";f.itemSpacing=0;f.clipsContent=false;
 f.fills=[{type:"SOLID",color:h2r("#fafafa")}];page.appendChild(f);f.x=x;f.y=0;return f;}
`;

// ═══════════════ 남은 6개 프레임 — 프리셋 결정표 ═══════════════
// (모든 ID 는 PRESETS.json 실존 ID. 토큰맵 T = {"#fafafa":BG,"#292929":TX,"#6c4cff":BT,"#f7f6f3":BG,"#333338":TX})

const PLAN = {
  "6-③-미니멀": {
    x: 40020, BG:"#EAE8E3", TX:"#212326", BT:"#35566B", dark:false,
    radius:0, side:32, btnR:0, TITLE:"S-Core Dream", BODY:"Pretendard", align:"LEFT",
    titlePreset:"4023:101",           // 좌 18
    sections:[
      ["히어로","5455:182","로고카드(children[0]) 제거 · 첫카드 pt36 · inject [eyebrow,제목,카피,null]"],
      ["핵심정보","5395:14800","repU(0,2,2,5) → 기간/장소/관람시간/휴관/관람료"],
      ["스토리","5484:27","LEFT · 기획 의도 2문단"],
      ["자료(작품 6점)","5408:219","repU(0,9,2,6) → 각 unit 에서 offset [8,4,3,1] 제거 → [갤러리,항목,2단,2단,2단] 5카드\n        inject/unit = [null, 작품명, '작가',작가, '재료',재료, '크기',크기]"],
      ["위치","5455:1249","inject [null,주소,'지도 보기'] · pb=8"],
      ["주차 안내","5484:27","CENTER · b36"],
      ["문의","5486:360","가로 2단 Outlined ['Call','Email']"]
    ]
  },
  "6-③-에디토리얼": {
    x: 40500, BG:"#211E1B", TX:"#E9E2D6", BT:"#BE9752", dark:true,
    radius:8, side:20, btnR:8, TITLE:"ChosunilboNM", BODY:"KoPub Batang", align:"LEFT",
    titlePreset:"4024:98",            // 좌 18 + 긴선
    sections:[
      ["헤더","4460:87","로고+구분선 · inject ['흐르는 것들']"],
      ["히어로","5455:262","풀블리드 이미지 · inject [null,'흐르는 것들','무심천 아트스페이스 2026 기획전\\n2026. 9. 2 — 10. 12 · 1·2 전시실']"],
      ["핵심정보","5408:418","2단 양끝 repU(0,1,3,5)"],
      ["스토리","5484:27","LEFT"],
      ["자료(작품 6점)","5408:582","repU(0,4,2,6) · unit=[이미지,항목22,세부13,세부15]\n        inject/unit = [null, 작품명, 작가, '재료 · 크기']"],
      ["위치","5486:349","inject [null,주소,'지도 보기'] · pb=8"],
      ["주차 안내","5484:27","b36"],
      ["문의","5455:1285","세로 2 — 위 채움 / 아래 Outlined ['전화하기','메일 보내기']"]
    ]
  },
  "6-③-볼드": {
    x: 40980, BG:"#C9D2CE", TX:"#1F2A28", BT:"#6E3B5C", dark:false,
    radius:0, side:20, btnR:100, TITLE:"Noto Serif KR", BODY:"Pretendard", align:"LEFT",
    titlePreset:"4649:127",           // 좌 라벨13 + 카피22 (텍스트 2개)
    sections:[
      ["헤더","3311:10497","솔리드: hdr.fills=BT 100% · 텍스트=BG · inject ['흐르는 것들']"],
      ["히어로","5455:359","inject [null,'무심천 아트스페이스 2026 기획전','흐르는 것들','2026. 9. 2 — 10. 12 · 1·2 전시실']"],
      ["핵심정보","5395:14800","repU(0,2,2,5)"],
      ["스토리","5484:23","LEFT"],
      ["자료(작품 6점)","5408:729","repU(0,8,2,6) → 각 unit offset [7,6] 제거 → [01,갤러리,항목,설명문구,2단,2단]\n        inject/unit = [번호, null, 작품명, 작가, '재료',재료, '크기',크기]"],
      ["위치","5455:1249","pb=8"],
      ["주차 안내","5484:23","b36"],
      ["문의","5455:1299","전폭 세로 2 · 틴트 10% ['전화하기','메일 보내기']"]
    ],
    titleLabels:[["관람 안내","전시 정보"],["기획 의도","이 전시에 대하여"],["작품 6점","출품 작품"],["청주 사직대로","전시장 오시는 길"],["문의","관람 문의"]]
  },
  "6-④-미니멀": {
    x: 41760, BG:"#EDEAE0", TX:"#2B2E27", BT:"#4F6B3A", dark:false,
    radius:8, side:32, btnR:8, TITLE:"Pretendard", BODY:"Gowun Dodum", align:"CENTER",
    titlePreset:"4023:96",            // 중앙 22
    numbering:"숫자 01~05",
    sections:[
      ["히어로","5455:182","헤더 없음 → 로고 카드 유지 · inject [null,'별빛언덕 오토캠핑장','처음 오시는 분을 위한\\n이용 안내','도착부터 퇴실까지, 순서대로 정리했습니다.',null]"],
      ["핵심정보","5395:14113","CENTER · repU(0,2,2,8) → 입실/퇴실/당일이용/주중/주말/성수기(요금 문의)/기준인원/인원추가"],
      ["나열(이용 순서 5단계)","5487:23","repU(0,1,3,5) · inject '01 예약하기\\n설명' (넘버는 항목 줄=제목폰트)"],
      ["자료(시설 3컷)","5395:14052","inject ['둘러보기',null,null,null,'사이트 22면 · 온수 개수대 · 관리동 매점']"],
      ["안내사항 4","5455:1199","구분선/부가설명 카드 제거 후 아이콘행 repU(0,1,3,4)"],
      ["FAQ 3","5487:23","repU(0,1,3,3) · '질문\\n답'"],
      ["위치","5455:1249","pb=8"],
      ["내비 안내","5484:27","b36"],
      ["문의","5486:360","가로 2단 Outlined ['Call','SMS']"]
    ]
  },
  "6-④-에디토리얼": {
    x: 42240, BG:"#1C2430", TX:"#E4E7EC", BT:"#D9A441", dark:true,
    radius:0, side:20, btnR:0, TITLE:"Noto Serif KR", BODY:"Pretendard", align:"LEFT",
    titlePreset:"4023:101",           // 좌 18
    numbering:"숫자 01~05 (앰버)",
    sections:[
      ["헤더","4460:87","로고+구분선 · inject ['별빛언덕 오토캠핑장'] → 히어로 로고 반복 ❌"],
      ["히어로","5455:262","inject [null,'처음 오시는 분을 위한\\n이용 안내','도착부터 퇴실까지, 순서대로 정리했습니다.']"],
      ["핵심정보","5408:418","repU(0,1,3,8)"],
      ["나열(5단계)","5408:448","repU(0,1,3,5) · inject/unit = [번호, '예약하기\\n설명']"],
      ["자료(3컷)","5395:14052",""],
      ["안내사항 4","5486:317","부가설명 카드 제거 후 repU(0,1,2,4)"],
      ["FAQ 3","5487:72","repU(0,1,3,3)"],
      ["위치","5486:349","pb=8"],
      ["내비 안내","5484:27","b36"],
      ["문의","5455:1285","세로 2 — 위 채움 / 아래 틴트 12% ['전화하기','문자 보내기']"]
    ]
  },
  "6-④-볼드": {
    x: 42720, BG:"#E9E1D2", TX:"#2A2318", BT:"#A8471A", dark:false,
    radius:0, side:20, btnR:100, TITLE:"Gmarket Sans TTF", BODY:"Pretendard", align:"LEFT",
    titlePreset:"4593:286",           // 상하선 (오른쪽 TEXT 삭제 후 사용)
    numbering:"🔤 이모지 📞 🚗 ⛺ 🌙 🧹 (3안 중 이모지 안)",
    sections:[
      ["헤더","3311:10494","솔리드 BT + BG 텍스트 · inject ['별빛언덕 오토캠핑장']"],
      ["히어로","5455:359","inject [null,'별빛언덕 오토캠핑장','처음 오시는 분을 위한\\n이용 안내','도착부터 퇴실까지, 순서대로 정리했습니다.']"],
      ["핵심정보","5395:14800","repU(0,2,2,8)"],
      ["나열(5단계·이모지)","5408:603","LEFT · repU(0,1,3,5) · inject '📞 예약하기\\n설명' (이모지가 제목 줄에 → 제목폰트)"],
      ["자료(3컷)","5395:12637","갤러리 3 + 캡션 3"],
      ["안내사항 4","5486:339","부가설명 카드 제거 후 repU(0,1,2,4)"],
      ["FAQ 3","5408:613","repU(0,1,3,3) · 2줄만 주입(3번째 줄 비움)"],
      ["위치","5455:1249","pb=8"],
      ["내비 안내","5484:23","b36"],
      ["문의","5455:1292","전폭 1단 채움 '전화하기' + 틴트 10% '문자 보내기' (버튼 3개 중 1개 삭제)"]
    ]
  }
};

// ═══ 마무리 순서 (프레임마다) ═══
// applyTokens(f,T,dark) → remapFonts(f,TITLE,BODY,18) → unify(f,radius,side,btnR)
// → 헤더 솔리드/틴트 · 문의 버튼 채움/틴트/Outlined 는 applyTokens '이후' 실제 hex 로 적용
// → 각 본문 섹션 b36() (타이틀·헤더·푸터 섹션 제외)
// → node.screenshot({contentsOnly:false}) 로 섹션별 육안 확인

// ═══ 알려진 함정 ═══
// 1) 혼합 스타일 TEXT 에 characters 를 그냥 대입하면 첫 글자 스타일로 평탄화된다 → injOne 사용 필수.
// 2) 히어로 프리셋 5455:454 는 제목·카피 카드 안쪽 프레임이 {버튼색} 솔리드 블록이다(의도된 색 히어로).
//    fill 을 지우면 글자색(={배경색})까지 안 보이게 되니 fill 을 지울 거면 글자색도 함께 바꿀 것.
// 3) 5455:1199(아이콘 안내사항)의 본문 TEXT 는 lsh=FIXED(192px) → layoutSizingHorizontal="FILL" 로 바꿔야 줄바꿈이 정상.
// 4) unify() 는 cornerRadius>=20 인 노드를 '버튼(pill)'로 보고 btnR 로 되돌린다.
//    각진 프리셋 버튼(반경<20)은 잡히지 않으므로 원형이 필요하면 버튼 프레임 radius 를 직접 100 으로.
// 5) 제목 36px + side 32 → 한 줄에 한글 8~9자. 히어로 제목은 명시 개행으로 어절 경계에서 끊을 것.
module.exports = { PRELUDE, PLAN };
