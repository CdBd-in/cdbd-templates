// margin-check.js — 「여백은 배경·테두리가 있느냐로 정한다」 자동 검사 (Figma 플러그인 API · use_figma에 붙여 실행)
// 정본 규칙: 1-6-2 「⚠️ 여백은 「배경·테두리가 있느냐」로 정한다」 + 「🎯 단일 depth 예외」 · CLAUDE.md 통일 8항목 ①(하한 20)
// 사용법·판정 근거·한계 = 같은 폴더 README.md
//
// 재는 법 — 패딩 값이 아니라 「화면에 실제로 놓인 위치」(절대 좌표)로 잰다. 섹션 자체 여백·여러 겹 래퍼가 있어도 결과가 같다.
//   · 글자 = 글상자 끝으로 잰다(긴 글이 들어오면 거기까지 차므로).
//     단 늘어나지 않는 표식(3글자 이하 — 번호·불릿·이모지)과 여러 칸 줄의 가운데 정렬 글자는 실제 잉크로 잰다(±2 허용).
//   · 배경 박스 = 채움·테두리가 있는 프레임. 이미지 자리(회색 박스·IMAGE 채움)와 페이지 배경과 같은 색 채움은 제외.
//   · 글자 하나짜리 낮은 박스(버튼·알약)는 안쪽 검사 제외.
//
// 판정 (카드 = 섹션 프레임의 직계 자식)
//  R1 배경 없는 글자·이미지·선이 화면 끝에서 20 미만 (이미지·선이 0 = 의도한 풀블리드라 통과)
//  R2 배경 박스가 화면 끝에서 20 미만 (양쪽 다 0 = 색 띠 → R5)
//  R3 배경 박스 안 글자가 박스 끝에서 16 미만 (화면 끝까지 닿는 띠 안은 20 미만)
//  R4 배경 없는 프레임이 겹겹이 여백을 가짐(래퍼 + 카드) — 하나로 합칠 것
//  R5 화면 끝까지 닿는 배경 박스(색 띠) — 허용 예외. 의도인지 「확인」만 (오류로 세지 않음)
//  R6 한 섹션 안 큰 박스(폭 180↑)들의 바깥 여백이 제각각 (색 띠와 안쪽 박스 혼재 포함)
//
// 입력 (셋 중 하나를 이 파일 앞에 선언)
//   const TARGET_IDS_IN = ['5395:14113', …]   섹션 id 목록 (라이브러리 = preset-index.json의 id)
//   const CONTAINER_ID_IN = '34:23'           이 노드 안의 380폭 섹션을 전부 (라이브러리 페이지)
//   const PAGE_IDS_IN = ['8100:23', …]        시안 페이지 프레임 — 그 직계 자식을 섹션으로 본다

const TARGET_IDS = typeof TARGET_IDS_IN !== 'undefined' ? TARGET_IDS_IN : [];
const CONTAINER_ID = typeof CONTAINER_ID_IN !== 'undefined' ? CONTAINER_ID_IN : null;
const PAGE_IDS = typeof PAGE_IDS_IN !== 'undefined' ? PAGE_IDS_IN : [];
const PAGE_W = 380, MIN = 20, INNER_MIN = 16, TOL = 2, BIG = 180;
const IMG_WORDS = /이미지|로고|영상|썸네일|비주얼|지도|사진|아이콘|프로필/;
const BTN_WORDS = /버튼|button|btn|cta/i;

const isVis = p => p.visible !== false && (p.opacity ?? 1) > 0.001;
const hasFill = n => Array.isArray(n.fills) && n.fills.some(isVis);
const hasStroke = n => Array.isArray(n.strokes) && n.strokes.some(isVis) && (n.strokeWeight || 0) > 0;
const isFrame = n => n.type === 'FRAME' || n.type === 'INSTANCE' || n.type === 'COMPONENT';
const solidKey = n => {
  const p = Array.isArray(n.fills) && n.fills.find(f => f.type === 'SOLID' && isVis(f));
  return p ? [p.color.r, p.color.g, p.color.b].map(v => Math.round(v * 255)).join(',') + '@' + Math.round((p.opacity ?? 1) * 100) : null;
};
function isImageBox(n) {
  if (n.type === 'TEXT') return false;
  if (Array.isArray(n.fills) && n.fills.some(p => p.type === 'IMAGE' && p.visible !== false)) return true;
  if (!hasFill(n)) return false;
  if (IMG_WORDS.test(n.name)) return true;
  const kids = 'children' in n ? n.children : [];
  const label = kids.find(c => c.type === 'TEXT');
  return !!(label && kids.length === 1 && IMG_WORDS.test(label.characters));
}
function boxed(n, bg) {
  if (!isFrame(n) || isImageBox(n)) return false;
  if (hasStroke(n)) return true;
  if (!hasFill(n)) return false;
  return !(n.fills.filter(isVis).length === 1 && solidKey(n) === bg);   // 페이지 배경과 같은 색 = 안 보이는 배경
}
const isLine = n => (n.type === 'LINE' || ((n.type === 'RECTANGLE' || n.type === 'VECTOR') && n.height <= 4)) && (hasFill(n) || hasStroke(n));
const pad = n => ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'].map(k => n[k] || 0);
function isButtonLike(b) {
  if (BTN_WORDS.test(b.name)) return true;
  return b.findAll(x => x.type === 'TEXT').length === 1 && b.height <= 64;
}
const isMarker = t => t.characters.trim().length <= 3;
const inRow = t => { const p = t.parent; return !!p && p.layoutMode === 'HORIZONTAL' && p.children.filter(k => k.visible !== false).length >= 2; };
function textEdges(t) {
  const ink = isMarker(t) || (t.textAlignHorizontal === 'CENTER' && inRow(t));
  const b = (ink && t.absoluteRenderBounds) ? t.absoluteRenderBounds : t.absoluteBoundingBox;
  return { l: b.x, r: b.x + b.width, ink };
}
const r0 = v => Math.round(v);

function checkSection(sec, bg) {
  const out = [];
  const sb = sec.absoluteBoundingBox, sx = sb.x, ex = sb.x + sb.width;
  const add = (node, rule, detail) => out.push({ rule, card: node.name, cardId: node.id, detail });
  const bigBoxes = [];
  for (const card of sec.children) {
    if (card.visible === false) continue;
    const recs = { texts: [], boxes: [], images: [] };
    (function walk(n, box) {
      if (n.visible === false) return;
      if (n.type === 'TEXT') { recs.texts.push({ n, box }); return; }
      if (isImageBox(n) || isLine(n)) { recs.images.push({ n, box }); return; }
      let nb = box;
      if (boxed(n, bg)) { recs.boxes.push({ n, parent: box }); nb = n; }
      if ('children' in n) for (const k of n.children) walk(k, nb);
    })(card, null);

    // 배경 박스 ↔ 화면 끝
    const bands = new Set();
    for (const { n: b, parent } of recs.boxes) {
      if (parent) continue;
      const bb = b.absoluteBoundingBox, gl = bb.x - sx, gr = ex - (bb.x + bb.width);
      if (gl <= 1 && gr <= 1) { bands.add(b); add(b, 'R5', `화면 끝까지 닿는 박스(폭 ${r0(bb.width)})`); }
      else if (gl < MIN - 0.5 || gr < MIN - 0.5) add(b, 'R2', `박스↔화면 ${r0(gl)}/${r0(gr)}`);
      if (bb.width >= BIG && !isButtonLike(b)) bigBoxes.push({ gl: r0(gl), gr: r0(gr), band: gl <= 1 && gr <= 1 });
    }
    // 글자 ↔ 박스(있으면) 또는 화면 끝
    for (const { n: t, box } of recs.texts) {
      if (!t.characters.trim()) continue;
      if (box && isButtonLike(box)) continue;
      const e = textEdges(t), tol = e.ink ? TOL : 0;
      const ref = box ? box.absoluteBoundingBox : sb;
      const band = !box || bands.has(box);
      const lim = band ? MIN : INNER_MIN;
      const gl = e.l - ref.x, gr = (ref.x + ref.width) - e.r;
      if (gl < lim - tol - 0.5 || gr < lim - tol - 0.5) {
        const s = `"${t.characters.slice(0, 12).replace(/\n/g, ' ')}"`;
        if (box) add(box, 'R3', `글자↔박스 ${r0(gl)}/${r0(gr)}${bands.has(box) ? ' (화면 끝 띠)' : ''} ${s}`);
        else add(card, 'R1', `글자↔화면 ${r0(gl)}/${r0(gr)} ${s}`);
      }
    }
    // 이미지·선 ↔ 화면 끝 (박스 밖 또는 색 띠 안만 — 0은 풀블리드라 통과)
    for (const { n: im, box } of recs.images) {
      if (box && !bands.has(box)) continue;
      const bb = im.absoluteBoundingBox, gl = bb.x - sx, gr = ex - (bb.x + bb.width);
      const bad = v => v > 1 && v < MIN - 0.5;
      if (bad(gl) || bad(gr)) add(card, 'R1', `${isLine(im) ? '선' : '이미지'}↔화면 ${r0(gl)}/${r0(gr)}`);
    }
    // R4 여백 두 겹 — 「자식 하나뿐인」 배경 없는 프레임이 겹쳐 있고 둘 이상이 여백을 가짐
    const chain = []; let n = card;
    while (isFrame(n) && !boxed(n, bg) && !isImageBox(n)) {
      chain.push(n);
      const kids = n.children.filter(k => k.visible !== false);
      if (kids.length === 1 && isFrame(kids[0])) n = kids[0]; else break;
    }
    const padded = chain.filter(f => pad(f).some(v => v > 0));
    if (padded.length >= 2) add(card, 'R4', padded.map(f => `${f.name}(${pad(f).join('/')})`).join(' > '));
  }
  // R6 한 섹션 안 큰 박스 바깥 여백
  if (bigBoxes.length >= 2) {
    const bandN = bigBoxes.filter(b => b.band).length, insets = bigBoxes.filter(b => !b.band);
    const vals = [...new Set(insets.map(b => `${b.gl}/${b.gr}`))];
    if (bandN && insets.length) out.push({ rule: 'R6', card: '-', detail: `색 띠 ${bandN} + 안쪽 박스 ${insets.length}(${vals.join(', ')}) 혼재` });
    else if (vals.length > 1) out.push({ rule: 'R6', card: '-', detail: `안쪽 박스 바깥 여백 제각각 ${vals.join(' · ')}` });
  }
  return out;
}

async function collectSections() {
  const list = [];   // [{ sec, bg }]
  for (const id of TARGET_IDS) { const n = await figma.getNodeByIdAsync(id); if (n) list.push({ sec: n, bg: solidKey(n) }); }
  for (const id of PAGE_IDS) {
    const pg = await figma.getNodeByIdAsync(id); if (!pg) continue;
    for (const s of pg.children) if (isFrame(s) && s.visible !== false) list.push({ sec: s, bg: solidKey(pg) });
  }
  if (CONTAINER_ID) {
    const root = await figma.getNodeByIdAsync(CONTAINER_ID);
    const secs = root.findAll(n => n.type === 'FRAME' && Math.round(n.width) === PAGE_W && n.parent && Math.round(n.parent.width || 0) !== PAGE_W);
    for (const s of secs) list.push({ sec: s, bg: solidKey(s) });
  }
  return list;
}

const sections = await collectSections();
const results = [];
for (const { sec, bg } of sections) {
  const f = checkSection(sec, bg);
  if (f.length) results.push({ section: sec.name, sectionId: sec.id, findings: f });
}
const summary = {}, sectionsPerRule = {};
for (const r of results) {
  const seen = new Set();
  for (const f of r.findings) { summary[f.rule] = (summary[f.rule] || 0) + 1; seen.add(f.rule); }
  for (const k of seen) sectionsPerRule[k] = (sectionsPerRule[k] || 0) + 1;
}
const errors = results.map(r => ({ ...r, findings: r.findings.filter(f => f.rule !== 'R5') })).filter(r => r.findings.length);
return {
  checked: sections.length,
  sectionsWithErrors: errors.length,
  summary, sectionsPerRule,
  errors,
  bandSections: results.filter(r => r.findings.some(f => f.rule === 'R5')).map(r => r.section),
};
