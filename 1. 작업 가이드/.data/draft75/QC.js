// ═══ 75안 최종 검수 전수 스윕 (읽기 전용) ═══
// use_figma 에 그대로 붙여 실행. 대상 페이지 5843:37
const page = await figma.getNodeByIdAsync("5843:37");
const frames = page.children.filter(c=>c.type==="FRAME" && /^\d-[①-⑥]-(미니멀|에디토리얼|볼드)/.test(c.name));
const r2h=c=>"#"+[c.r,c.g,c.b].map(v=>Math.round(v*255).toString(16).padStart(2,"0")).join("");
const h2r=h=>{h=h.replace("#","");return{r:parseInt(h.slice(0,2),16)/255,g:parseInt(h.slice(2,4),16)/255,b:parseInt(h.slice(4,6),16)/255};};
const lum=h=>{const c=h2r(h);const f=v=>v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);return .2126*f(c.r)+.7152*f(c.g)+.0722*f(c.b);};
const ratio=(a,b)=>{const A=lum(a),B=lum(b);return Math.round(((Math.max(A,B)+.05)/(Math.min(A,B)+.05))*100)/100;};

const PLACE=/^(제목|본문 텍스트|세부 정보|항목|LABEL|label|버튼 텍스트|소개 문구|안내 문구|설명 문구|카피 혹은|페이지 제목|EYEBROW|상품명|가격|프로모션 내용|프로모션 제목|안내 사항|세션 제목|00|00,000원|00단위|이미지|메인 이미지|서브 이미지|아이콘|로고)/;
const out=[];
for(const f of frames){
  const radii=new Set(), pads=new Set(), fonts=new Set(), sizes=[];
  let place=0, texts=0, btnRadii=new Set();
  const walk=n=>{
    if("cornerRadius" in n && typeof n.cornerRadius==="number"){
      if(/버튼|button|btn/i.test(n.name)) btnRadii.add(n.cornerRadius); else if(n!==f) radii.add(n.cornerRadius);
    }
    if(n.type==="TEXT"){
      texts++;
      const c=n.characters.trim();
      if(PLACE.test(c) && c.length<24) place++;
      for(const s of n.getStyledTextSegments(["fontName","fontSize"])){ fonts.add(s.fontName.family); sizes.push(s.fontSize); }
    }
    if(n.children) n.children.forEach(walk);
  };
  walk(f);
  // 섹션 = 직계 자식 · 각 섹션 마지막 카드 pb
  const secLast=[];
  for(const sec of f.children){
    const k=sec.children;
    if(k&&k.length&&"paddingBottom" in k[k.length-1]) secLast.push(k[k.length-1].paddingBottom);
    else if("paddingBottom" in sec) secLast.push(sec.paddingBottom);
  }
  // 좌우 여백
  for(const sec of f.children) for(const card of (sec.children||[])) if("paddingLeft" in card && card.paddingLeft>0) pads.add(card.paddingLeft);
  const bg = (Array.isArray(f.fills)&&f.fills[0]&&f.fills[0].type==="SOLID")?r2h(f.fills[0].color):null;
  out.push({name:f.name, id:f.id, h:Math.round(f.height), secs:f.children.length,
    radii:[...radii], btn:[...btnRadii], pads:[...pads],
    pb36: secLast.filter(v=>v!==36).length, pbVals:[...new Set(secLast)],
    fonts:[...fonts], maxSizes:[...new Set(sizes)].sort((a,b)=>b-a).slice(0,4),
    place, texts, bg});
}
return JSON.stringify({count:frames.length, rows:out});
