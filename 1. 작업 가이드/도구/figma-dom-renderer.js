function hx(h){h=h.replace('#','');if(h.length===3)h=h.split('').map(c=>c+c).join('');return {r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};}
function col(v){v=(v||'').trim();
  if(v[0]==='#'){const c=hx(v);return {c:c,a:1};}
  const m=v.match(/rgba?\(([^)]+)\)/); if(m){const p=m[1].split(',').map(x=>parseFloat(x));return {c:{r:p[0]/255,g:p[1]/255,b:p[2]/255},a:p[3]===undefined?1:p[3]};}
  return {c:{r:0,g:0,b:0},a:1};}
function solid(v){const o=col(v);return {type:'SOLID',color:o.c,opacity:o.a};}
function paintFrom(v){ if(!v) return [];
  v=String(v).trim();
  if(v.indexOf('linear-gradient')===0){ const cs=v.match(/#[0-9a-fA-F]{3,6}/g)||['#dddddd'];
    if(cs.length>=2){const a=col(cs[0]),b=col(cs[1]);
      return [{type:'GRADIENT_LINEAR',gradientTransform:[[0.6,0.8,0],[-0.8,0.6,0.6]],gradientStops:[{position:0,color:{r:a.c.r,g:a.c.g,b:a.c.b,a:1}},{position:1,color:{r:b.c.r,g:b.c.g,b:b.c.b,a:1}}]}];}
    return [solid(cs[0])]; }
  if(v==='none'||v==='transparent') return [];
  return [solid(v)];}
function num(v){ if(v===undefined||v===null) return 0; const m=String(v).match(/-?[\d.]+/); return m?parseFloat(m[0]):0; }
function px4(v){ if(!v) return [0,0,0,0]; const p=String(v).replace(/px/g,'').trim().split(/\s+/).map(parseFloat);
  if(p.length===1)return [p[0],p[0],p[0],p[0]]; if(p.length===2)return [p[0],p[1],p[0],p[1]]; if(p.length===3)return [p[0],p[1],p[2],p[1]]; return p.slice(0,4);}
const INH=['font-size','font-weight','font-family','color','text-align','line-height'];
function merge(inh,st){const o={};for(const k in inh)o[k]=inh[k];for(const k of INH) if(st[k]!==undefined)o[k]=st[k];return o;}
function wmap(w,serif){const n=parseInt(w)||400; if(n<=300)return 'Light'; if(n<=400)return 'Regular'; if(n<=500)return 'Medium'; if(n<=600)return 'SemiBold'; if(n<=700)return 'Bold'; return serif?'Bold':'ExtraBold';}
async function loadAll(){
  for(const s of ['Light','Regular','Medium','SemiBold','Bold','ExtraBold']){try{await figma.loadFontAsync({family:'Pretendard',style:s});}catch(e){}}
  for(const s of ['Light','Regular','Medium','SemiBold','Bold']){try{await figma.loadFontAsync({family:'Cormorant Garamond',style:s});}catch(e){}}
  for(const s of ['Light','Regular','Medium','SemiBold','Bold','Black']){try{await figma.loadFontAsync({family:'Noto Serif KR',style:s});}catch(e){}}
  for(const s of ['Regular','Bold']){try{await figma.loadFontAsync({family:'Gowun Batang',style:s});}catch(e){}}
}
function hasKo(s){return /[\uAC00-\uD7A3]/.test(s);}
// CSS font-family \uBB38\uC790\uC5F4 \u2192 Figma \uC2E4\uC7AC \uD3F0\uD2B8.
// \uB098\uB214\uBA85\uC870\u00B7\uB098\uB214\uACE0\uB515\uC740 Figma\uC5D0 \uC5C6\uB2E4(1-4. \uD3F0\uD2B8 47\uD589) \u2192 \uBCF8\uBA85\uC870(Noto Serif KR)\uB85C \uB300\uCCB4.
// CdBd \uC5D0\uB514\uD130\uC5D0\uB294 \uB098\uB214\uBA85\uC870\uAC00 \uC788\uC73C\uBBC0\uB85C 4\uB2E8\uACC4\uC5D0\uC11C \uC6D0\uB798 \uD3F0\uD2B8\uB85C \uB418\uB3CC\uB9B0\uB2E4.
const SERIF_RE=/nanum\s*myeongjo|myeongjo|batang|serif|cormorant|garamond|instrument|times|georgia/i;
const LATIN_SERIF_RE=/cormorant|garamond|instrument|times|georgia/i;
function isSerifFam(fam){return SERIF_RE.test(String(fam||''));}
function famOf(fam,txt){
  fam=String(fam||'');
  if(!isSerifFam(fam)) return 'Pretendard';
  if(hasKo(txt)) return 'Noto Serif KR';                 // \uD55C\uAE00 \uBA85\uC870
  if(LATIN_SERIF_RE.test(fam)) return 'Cormorant Garamond'; // \uB77C\uD2F4 \uC804\uC6A9 \uC138\uB9AC\uD504
  return 'Noto Serif KR';                                 // \uB098\uB214\uBA85\uC870 \uACC4\uC5F4\uC758 \uB77C\uD2F4\uB3C4 \uBCF8\uBA85\uC870\uB85C \uD1B5\uC77C
}
function mkText(txt,inh){
  const serif=isSerifFam(inh['font-family']); const fam=famOf(inh['font-family'],txt);
  const t=figma.createText(); t.fontName={family:fam,style:wmap(inh['font-weight'],serif)};
  t.characters=txt; t.fontSize=num(inh['font-size'])||14;
  t.fills=paintFrom(inh['color']||'#222222'); t.textAutoResize='HEIGHT';
  if(inh['line-height']!==undefined) t.lineHeight={unit:'PERCENT',value:Math.round((num(inh['line-height'])||1.4)*100)};
  t.textAlignHorizontal=inh['text-align']==='center'?'CENTER':(inh['text-align']==='right'?'RIGHT':'LEFT');
  return t;
}
// CSS border → Figma stroke.
// ⚠️ 예전엔 box-shadow:inset 만 테두리로 인식했다 → border / border-top 으로 그린 구분선이 전부 사라졌다.
// 한 줄짜리 구분선(border-top)은 Figma 개별 변 두께(strokeTopWeight 등)로 재현한다.
function parseBorder(v){ v=String(v||'').trim(); if(!v||v==='none'||v.indexOf('none')===0) return null;
  const w=v.match(/^([\d.]+)px/); const c=v.match(/rgba?\([^)]*\)|#[0-9a-fA-F]{3,6}/);
  if(!w||!c) return null; const px=parseFloat(w[1]); if(!(px>0)) return null;
  return {w:px, c:c[0]}; }
function applyBorders(f,st){
  const all=parseBorder(st.border);
  const sides={top:parseBorder(st['border-top']),right:parseBorder(st['border-right']),
               bottom:parseBorder(st['border-bottom']),left:parseBorder(st['border-left'])};
  const any=all||sides.top||sides.right||sides.bottom||sides.left;
  if(!any) return;
  try{ f.strokes=[solid(any.c)]; f.strokeAlign='INSIDE'; }catch(e){ return; }
  if(all && !sides.top && !sides.right && !sides.bottom && !sides.left){
    try{ f.strokeWeight=all.w; }catch(e){}
    return;
  }
  // 변별 두께 (지정 안 된 변은 border 일괄값, 그것도 없으면 0)
  const base=all?all.w:0;
  try{
    f.strokeTopWeight    = sides.top    ? sides.top.w    : base;
    f.strokeRightWeight  = sides.right  ? sides.right.w  : base;
    f.strokeBottomWeight = sides.bottom ? sides.bottom.w : base;
    f.strokeLeftWeight   = sides.left   ? sides.left.w   : base;
  }catch(e){ try{ f.strokeWeight=any.w; }catch(e2){} }
}
function isInline(c){const s=c.style||{}; return (c.tag==='span'||c.tag==='b'||c.tag==='strong'||c.tag==='br') && !s.background && !s.padding && !s['border-radius'] && !s.display;}
function collectSegs(n,inh,out){ const i2=merge(inh,n.style||{});
  for(const c of (n.children||[])){ if(c.tag==='#text') out.push({t:c.text,inh:i2}); else if(c.tag==='br') out.push({t:'\n',inh:i2}); else collectSegs(c,i2,out); } return out; }
function mkInline(n,inh){ const segs=collectSegs(n,inh,[]); if(!segs.length) return null;
  let full=''; const ranges=[];
  for(const s of segs){ const start=full.length; const piece=(s.t==='\n')?'\n':((full && !full.endsWith('\n'))?' ':'')+s.t; full+=piece; ranges.push({a:start+(piece.length-s.t.length),b:full.length,inh:s.inh}); }
  const base=segs[0].inh; const t=mkText(full,base);
  for(const rg of ranges){ if(rg.a>=rg.b) continue; const ih=rg.inh; const serif=isSerifFam(ih['font-family']);
    const fam=famOf(ih['font-family'], full.slice(rg.a,rg.b));
    try{ t.setRangeFontName(rg.a,rg.b,{family:fam,style:wmap(ih['font-weight'],serif)}); }catch(e){}
    try{ if(ih['font-size']!==undefined) t.setRangeFontSize(rg.a,rg.b,num(ih['font-size'])); }catch(e){}
    try{ if(ih['color']) t.setRangeFills(rg.a,rg.b,paintFrom(ih['color'])); }catch(e){}
  }
  return t; }
function render(n,inh){
  const st=n.style||{}; const inh2=merge(inh,st);
  if(n.tag==='image-slot'){
    const f=figma.createAutoLayout('VERTICAL'); f.name='이미지 슬롯';
    f.fills=[{type:'SOLID',color:{r:0.898,g:0.867,b:0.816}}];
    f.primaryAxisAlignItems='CENTER'; f.counterAxisAlignItems='CENTER';
    f.paddingTop=10;f.paddingBottom=10;f.paddingLeft=14;f.paddingRight=14; f.itemSpacing=0;
    if(n.shape==='circle'){ f.cornerRadius=999; }
    const t=mkText('🖼  '+(n.ph_text||'이미지'), {'font-size':'12','color':'#8A7F6E','text-align':'center','line-height':'1.4'});
    f.appendChild(t); try{t.layoutSizingHorizontal='FILL';}catch(e){}
    return f;
  }
  const texts=(n.children||[]).filter(c=>c.tag==='#text');
  const elems=(n.children||[]).filter(c=>c.tag!=='#text');
  const hasBorder=!!(st.border||st['border-top']||st['border-right']||st['border-bottom']||st['border-left']);
  const hasBox=st.background||st.padding||st['border-radius']||st['box-shadow']||hasBorder||st.display==='flex';
  const inlineOnly=elems.length>0 && elems.every(isInline);
  if(texts.length && !elems.length && !hasBox){ return mkText(texts.map(t=>t.text).join(' '),inh2); }
  if(texts.length && inlineOnly && !hasBox){ return mkInline(n,inh); }
  const grid=(st.display==='grid');
  const row=grid||(st.display==='flex' && st['flex-direction']!=='column');
  const f=figma.createAutoLayout(row?'HORIZONTAL':'VERTICAL');
  if(grid||st['flex-wrap']==='wrap'){ try{ f.layoutWrap='WRAP'; f.counterAxisSpacing=num(st.gap); }catch(e){} }
  f.name=n.tag||'div'; f.fills=paintFrom(st.background);
  const p=px4(st.padding); f.paddingTop=p[0];f.paddingRight=p[1];f.paddingBottom=p[2];f.paddingLeft=p[3];
  if(st.gap) f.itemSpacing=num(st.gap); else f.itemSpacing=0;
  if(st['border-radius']) f.cornerRadius=Math.min(num(st['border-radius']),999);
  if(st['border-radius'] && (st.overflow==='hidden'||st['overflow-x']==='hidden')){ try{f.clipsContent=true;}catch(e){} }
  if(st['box-shadow'] && String(st['box-shadow']).indexOf('inset')>=0){ const c=(String(st['box-shadow']).match(/rgba?\([^)]*\)|#[0-9a-fA-F]{3,6}/)||[])[0]; if(c){ f.strokes=[solid(c)]; f.strokeWeight=1; f.strokeAlign='INSIDE'; } }
  applyBorders(f,st);
  if(st['justify-content']==='space-between') f.primaryAxisAlignItems='SPACE_BETWEEN';
  const jcC=(st['justify-content']==='center'); if(jcC) f.primaryAxisAlignItems='CENTER';
  if(st['align-items']==='center') f.counterAxisAlignItems='CENTER';
  if(st['text-align']==='center' && !row) f.counterAxisAlignItems='CENTER';
  if(texts.length && inlineOnly){ const ti=mkInline(n,inh2); if(ti){ f.appendChild(ti); if(!jcC){ try{ti.layoutSizingHorizontal='FILL';}catch(e){} } return f; } }
  const abs=[];
  for(const c of (n.children||[])){
    if(c.tag==='#text'){ const t=mkText(c.text,inh2); f.appendChild(t); if(!jcC){ try{t.layoutSizingHorizontal='FILL';}catch(e){} } continue; }
    const child=render(c,inh2); if(!child) continue;
    const cst=c.style||{};
    if(cst.position==='absolute'){ abs.push({node:child,st:cst}); f.appendChild(child); continue; }
    // margin 지원: Figma 오토레이아웃엔 margin이 없으므로 앞뒤에 투명 스페이서를 끼운다.
    // (padding으로 접으면 배경 있는 요소 — 예: height:1px 구분선 — 이 두꺼워진다)
    const mg=px4(cst.margin); const vertical=!row;
    const spacer=(px)=>{ const s=figma.createAutoLayout('VERTICAL'); s.name='margin'; s.fills=[];
      s.itemSpacing=0; s.paddingTop=0;s.paddingRight=0;s.paddingBottom=0;s.paddingLeft=0;
      s.counterAxisSizingMode='FIXED'; s.resize(vertical?f.width||1:px, vertical?px:(f.height||1));
      s.primaryAxisSizingMode='FIXED'; return s; };
    if(vertical && mg[0]>0){ const s=spacer(mg[0]); f.appendChild(s); try{s.layoutSizingHorizontal='FILL'; s.layoutSizingVertical='FIXED'; s.resize(s.width,mg[0]);}catch(e){} }
    f.appendChild(child);
    try{
      if(grid && c.w){ child.layoutSizingHorizontal='FIXED'; child.resize(c.w, c.h||child.height); }
      else if(cst.width && String(cst.width).indexOf('px')>0){ child.layoutSizingHorizontal='FIXED'; child.resize(num(cst.width), c.h||num(cst.height)||child.height); }
      else if(c.tag==='span'){ try{child.layoutSizingHorizontal='HUG';}catch(e){} }
      else { child.layoutSizingHorizontal='FILL'; }
      if(cst.height && String(cst.height).indexOf('px')>0){ try{ child.layoutSizingVertical='FIXED'; child.resize(child.width, num(cst.height)); }catch(e){} }
      else if(cst['min-height']){ try{ child.layoutSizingVertical='FIXED'; child.resize(child.width, num(cst['min-height'])); }catch(e){} }
    }catch(e){}
    if(c.h){ try{ child.layoutSizingVertical='FIXED'; child.resize(child.width, c.h); }catch(e){} }
    if(vertical && mg[2]>0){ const s=spacer(mg[2]); f.appendChild(s); try{s.layoutSizingHorizontal='FILL'; s.layoutSizingVertical='FIXED'; s.resize(s.width,mg[2]);}catch(e){} }
  }
  for(const a of abs){ try{ a.node.layoutPositioning='ABSOLUTE';
      const L=num(a.st.left), B=num(a.st.bottom), T=num(a.st.top);
      a.node.x=L; a.node.y=(a.st.bottom!==undefined)?(f.height-a.node.height-B):T;
      a.node.constraints={horizontal:'MIN',vertical:(a.st.bottom!==undefined)?'MAX':'MIN'};
    }catch(e){} }
  return f;
}
async function buildPhone(D,X,Y,opts){
  opts=opts||{}; await loadAll(); const th=D.theme;
  let phone;
  if(opts.phoneId){ phone=await figma.getNodeByIdAsync(opts.phoneId); }
  else { phone=figma.createAutoLayout('VERTICAL'); phone.name=th.name; phone.x=X; phone.y=Y; phone.itemSpacing=0;
    phone.paddingTop=0;phone.paddingBottom=0;phone.paddingLeft=0;phone.paddingRight=0;
    phone.counterAxisSizingMode='FIXED'; phone.resize(390,200); phone.primaryAxisSizingMode='AUTO'; phone.fills=paintFrom(th.bg); }
  const _from=opts.from||0,_to=(opts.to==null?D.cards.length:opts.to);
  for(let i=_from;i<_to;i++){ const cd=D.cards[i];
    const wrap=figma.createAutoLayout('VERTICAL'); wrap.name='카드: '+cd.type; wrap.fills=[]; wrap.itemSpacing=0;
    for(const c of (cd.tree.children||[])){ const nd=render(c,{}); if(nd){ wrap.appendChild(nd); try{nd.layoutSizingHorizontal='FILL';}catch(e){} if(c.h){try{nd.layoutSizingVertical='FIXED'; nd.resize(nd.width,c.h);}catch(e){}} } }
    phone.appendChild(wrap); try{wrap.layoutSizingHorizontal='FILL';}catch(e){}
  }
  return {id:phone.id,name:phone.name,h:Math.round(phone.height),built:_to,total:D.cards.length,done:_to>=D.cards.length};
}
