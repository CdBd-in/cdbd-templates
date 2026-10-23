// margin-check.js — 「여백은 배경·테두리가 있느냐로 정한다」 자동 검사 (Figma 플러그인 API · use_figma에 붙여 실행)
// 정본 규칙: 1-6-2 「⚠️ 여백은 「배경·테두리가 있느냐」로 정한다」 + 「🎯 단일 depth 예외」 · CLAUDE.md 통일 8항목 ①(하한 20)
// 사용: TARGET_IDS에 섹션(380폭 프레임) id 목록, 또는 CONTAINER_ID에 섹션들이 든 프레임/섹션/페이지 id를 넣고 실행
//       → { summary: 규칙별 건수, findings: [{section, card, rule, detail}] } 반환
//
// 판정 (카드 = 섹션 프레임의 직계 자식)
//  R1 배경 없는 카드 좌우 여백 < 20          (풀블리드 이미지·구분선 두께 0 여백 카드는 제외)
//  R2 배경 카드의 바깥 여백(감싸는 프레임 좌우) < 20
//  R3 배경 카드의 안쪽 여백 좌우 0 (글자가 박스 끝에 붙음 · 이미지만 든 박스는 제외)
//  R4 배경 없는데 여백 두 겹 (감싸는 프레임 + 채움 없는 안쪽 프레임 둘 다 좌우 여백)
//  R5 감싸는 프레임 없이 화면 끝까지 닿는 배경 박스 — 의도한 풀블리드(색 밴드)인지 「확인」 (오류 아님)

const TARGET_IDS = typeof TARGET_IDS_IN !== 'undefined' ? TARGET_IDS_IN : [];
const CONTAINER_ID = typeof CONTAINER_ID_IN !== 'undefined' ? CONTAINER_ID_IN : null;
const PAGE_W = 380, MIN = 20;
const IMG_WORDS = /이미지|로고|영상|썸네일|비주얼|지도|사진|아이콘|프로필/;

function hasFill(n) {
  return Array.isArray(n.fills) && n.fills.some(p => p.visible !== false && (p.opacity ?? 1) > 0.001);
}
function hasStroke(n) {
  return Array.isArray(n.strokes) && n.strokes.some(p => p.visible !== false) && (n.strokeWeight || 0) > 0;
}
function isImageBox(n) {
  // 이미지 자리(회색 채움·IMAGE 채움) = 카드 배경이 아니라 내용
  if (Array.isArray(n.fills) && n.fills.some(p => p.type === 'IMAGE')) return true;
  if (IMG_WORDS.test(n.name)) return true;
  const label = 'children' in n ? n.children.find(c => c.type === 'TEXT') : null;
  return !!(label && IMG_WORDS.test(label.characters) && n.children.length === 1);
}
function boxed(n) { return (hasFill(n) || hasStroke(n)) && !isImageBox(n); }
function hasText(n) { return 'findOne' in n && !!n.findOne(x => x.type === 'TEXT' && !IMG_WORDS.test(x.characters)); }
function lr(n) { return [n.paddingLeft || 0, n.paddingRight || 0]; }
function isSpacer(n) { return /구분선|여백/.test(n.name) && !hasText(n); }

function checkSection(sec) {
  const out = [];
  const add = (card, rule, detail) => out.push({ section: sec.name, sectionId: sec.id, card: card.name, cardId: card.id, rule, detail });
  for (const c of sec.children) {
    if (c.type !== 'FRAME' && c.type !== 'INSTANCE') continue;
    const [l, r] = lr(c);
    if (boxed(c)) {
      // 감싸는 프레임 없이 박스가 바로 섹션에 붙음
      if (Math.round(c.width) >= PAGE_W - 1) add(c, 'R5', `화면 끝까지 닿는 박스(폭 ${Math.round(c.width)}) — 의도한 색 밴드인지 확인`);
      else add(c, 'R2', `감싸는 프레임 없는 박스 · 폭 ${Math.round(c.width)}`);
      if (hasText(c) && (l === 0 || r === 0)) add(c, 'R3', `안쪽 좌우 ${l}/${r}`);
      continue;
    }
    const frames = 'children' in c ? c.children.filter(k => k.type === 'FRAME' || k.type === 'INSTANCE') : [];
    const box = frames.length === 1 && boxed(frames[0]) && Math.abs(frames[0].width - (c.width - l - r)) < 2 ? frames[0] : null;
    if (box) {
      if (l < MIN || r < MIN) add(c, 'R2', `바깥 좌우 ${l}/${r}`);
      const [bl, br] = lr(box);
      if (hasText(box) && (bl === 0 || br === 0)) add(box, 'R3', `안쪽 좌우 ${bl}/${br}`);
      continue;
    }
    // 배경 없는 카드
    const fullBleedImage = frames.some(k => isImageBox(k) && Math.round(k.width) >= PAGE_W - 1);
    if (!fullBleedImage && !isSpacer(c) && (l < MIN || r < MIN)) add(c, 'R1', `좌우 ${l}/${r}`);
    if (frames.length === 1 && !boxed(frames[0]) && !isImageBox(frames[0])) {
      const [il, ir] = lr(frames[0]);
      if ((il > 0 || ir > 0) && (l > 0 || r > 0)) add(c, 'R4', `바깥 ${l}/${r} + 안쪽 ${il}/${ir}`);
    }
  }
  return out;
}

async function collectSections() {
  if (TARGET_IDS.length) {
    const arr = [];
    for (const id of TARGET_IDS) { const n = await figma.getNodeByIdAsync(id); if (n) arr.push(n); }
    return arr;
  }
  const root = await figma.getNodeByIdAsync(CONTAINER_ID);
  return root.findAll(n => n.type === 'FRAME' && Math.round(n.width) === PAGE_W && n.parent && Math.round(n.parent.width || 0) !== PAGE_W);
}

const sections = await collectSections();
const findings = [];
for (const s of sections) findings.push(...checkSection(s));
const summary = {};
for (const f of findings) summary[f.rule] = (summary[f.rule] || 0) + 1;
const sectionsHit = {};
for (const f of findings) if (f.rule !== 'R5') sectionsHit[f.section] = true;
return { checked: sections.length, sectionsWithErrors: Object.keys(sectionsHit).length, summary, findings };
