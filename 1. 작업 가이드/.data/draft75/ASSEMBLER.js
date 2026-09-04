// ═══ CdBd 75안 조립 표준 엔진 (2026-09-04) ═══
// use_figma 호출 안에 이 블록을 그대로 붙여넣고 아래 "조립부"만 바꿔 쓴다.
// fileKey = 24O01lprp5i2ufl7CbZXXx · 대상 페이지 = 5843:37 · 프리셋 페이지 = 34:23

const h2r=h=>{h=h.replace("#","");return{r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};};
const r2h=c=>"#"+[c.r,c.g,c.b].map(v=>Math.round(v*255).toString(16).padStart(2,"0")).join("");
const lum=h=>{const c=h2r(h);const f=v=>v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);return 0.2126*f(c.r)+0.7152*f(c.g)+0.0722*f(c.b);};
const ratio=(a,b)=>{const A=lum(a),B=lum(b);return Math.round(((Math.max(A,B)+0.05)/(Math.min(A,B)+0.05))*100)/100;};

let STYLES=null;
async function initFonts(){ if(STYLES)return; STYLES={};
  (await figma.listAvailableFontsAsync()).forEach(f=>{(STYLES[f.fontName.family]=STYLES[f.fontName.family]||[]).push(f.fontName.style);}); }
const RANK=["Thin","ExtraLight","Light","3 Light","DemiLight","Regular","4 Regular","Medium","5 Medium","SemiBold","6 Bold","Bold","ExtraBold","7 ExtraBold","Black"];
function pickStyle(fam,want){const a=STYLES[fam]||[];if(!a.length)return null;if(a.includes(want))return want;
  const wi=RANK.indexOf(want);if(wi<0)return a[0];let b=a[0],bd=99;
  for(const s of a){const i=RANK.indexOf(s);if(i<0)continue;const d=Math.abs(i-wi);if(d<bd){bd=d;b=s;}}return b;}
async function setFont(fam,want){const st=pickStyle(fam,want);if(!st)return null;const fn={family:fam,style:st};await figma.loadFontAsync(fn);return fn;}

// ── 토큰 치환 (불투명도 보존 · 다크는 틴트 +2%p / 선 +10%p) ──
function mapArr(arr,T,dark){return arr.map(p=>{if(p.type!=="SOLID")return p;const to=T[r2h(p.color)];if(!to)return p;
  let o=p.opacity===undefined?1:p.opacity;
  if(dark&&o<1) o=Math.min(1,o+0.02);
  return {...p,color:h2r(to),opacity:o};});}
function applyTokens(n,T,dark){
  if("fills" in n && Array.isArray(n.fills)) n.fills=mapArr(n.fills,T,dark);
  if("strokes" in n && Array.isArray(n.strokes)){
    const s=mapArr(n.strokes,T,dark);
    n.strokes = dark ? s.map(p=>p.type==="SOLID"&&p.opacity!==undefined&&p.opacity<1?{...p,opacity:Math.min(1,p.opacity+0.10)}:p) : s;
  }
  if(n.type==="TEXT" && !Array.isArray(n.fills)){
    for(const s of n.getStyledTextSegments(["fills"])) n.setRangeFills(s.start,s.end,mapArr(s.fills,T,dark));
  }
  if(n.children) n.children.forEach(c=>applyTokens(c,T,dark));
}

// ── 폰트 매핑 (구분자 런은 원본 유지) ──
function texts(n){const o=[];const w=x=>{if(x.type==="TEXT")o.push(x);if(x.children)x.children.forEach(w);};w(n);return o;}
async function remapFonts(n,TITLE,BODY,titleMin){
  for(const t of texts(n)){
    for(const s of t.getStyledTextSegments(["fontName","fontSize"])){
      await figma.loadFontAsync(s.fontName);
      if(/^[—–―·•\s]+$/.test(t.characters.slice(s.start,s.end))) continue;   // 구분자 = Pretendard 유지
      const fam=(s.fontSize>=titleMin||/Bold|Black|ExtraBold/.test(s.fontName.style))?TITLE:BODY;
      const fn=await setFont(fam,s.fontName.style);
      if(fn) t.setRangeFontName(s.start,s.end,fn);
    }
  }
}

// ── 텍스트 주입 (문서 순서 · null이면 건너뜀) ──
async function inject(node,arr){
  const ts=texts(node);
  for(let i=0;i<ts.length&&i<arr.length;i++){
    if(arr[i]===null||arr[i]===undefined) continue;
    for(const s of ts[i].getStyledTextSegments(["fontName"])) await figma.loadFontAsync(s.fontName);
    ts[i].characters=String(arr[i]);
  }
  return ts.length;
}

// ── 반복 항목 개수 맞추기 (프리셋의 반복 카드를 복제/삭제) ──
// repeatFrom~repeatTo (0-based, 포함) 가 반복 단위. 마지막 카드 pb는 보존.
function setRepeat(preset,repeatFrom,repeatTo,want){
  const kids=preset.children;
  const unit=repeatTo-repeatFrom+1;
  const have=unit;
  const gapPb=kids[repeatFrom].paddingBottom;      // 항목 간 간격
  const lastPb=kids[repeatTo].paddingBottom;       // 마지막 항목 여백(보통 36 또는 gap)
  if(want>have){
    for(let i=have;i<want;i++){
      const c=kids[repeatFrom].clone();
      preset.insertChild(repeatFrom+i,c);
      try{c.layoutSizingHorizontal="FILL";}catch(e){}
    }
  } else if(want<have){
    for(let i=have-1;i>=want;i--) kids[repeatFrom+i].remove();
  }
  // pb 재정렬: 마지막 반복만 lastPb, 나머지는 gapPb
  for(let i=0;i<want;i++){
    const c=preset.children[repeatFrom+i];
    if("paddingBottom" in c) c.paddingBottom = (i===want-1)?lastPb:gapPb;
  }
}

// ── 통일 스윕 ──
// radius: 0(각진)|8(둥근) · side: 좌우 여백(미니멀32/에디20/볼드20) · 버튼은 모양 유지
function unify(root,radius,side){
  const w=n=>{
    if("cornerRadius" in n && typeof n.cornerRadius==="number" && !/버튼|button|btn/i.test(n.name)){
      try{n.cornerRadius=radius;}catch(e){}
    }
    if(n.children)n.children.forEach(w);
  };
  w(root);
  if(side!==null&&side!==undefined){
    for(const sec of root.children) for(const card of (sec.children||[])){
      if("paddingLeft" in card && card.paddingLeft>0){ card.paddingLeft=side; card.paddingRight=side; }
    }
  }
}
// 섹션 마지막 카드 하단 = 36
function bottom36(section){
  const k=section.children; if(!k||!k.length)return;
  const last=k[k.length-1];
  if("paddingBottom" in last) last.paddingBottom=36;
}

// ── 시안 프레임 만들기 ──
async function newDraft(page,name,x,y,bg){
  const f=figma.createFrame(); f.name=name; f.resize(380,100);
  f.layoutMode="VERTICAL"; f.primaryAxisSizingMode="AUTO"; f.counterAxisSizingMode="FIXED";
  f.itemSpacing=0; f.clipsContent=false;
  f.fills=[{type:"SOLID",color:h2r(bg)}];
  page.appendChild(f); f.x=x; f.y=y; return f;
}
// ── 프리셋 붙이기 ──
async function put(frame,presetId){
  const p=await figma.getNodeByIdAsync(presetId);
  const c=p.clone(); frame.appendChild(c);
  try{c.layoutSizingHorizontal="FILL";}catch(e){}
  return c;
}
