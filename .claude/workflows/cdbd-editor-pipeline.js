export const meta = {
  name: 'cdbd-editor-pipeline',
  description: 'CdBd 4단계: Figma 시안을 CdBd 에디터에 생성→검증→수정 (13 스코프)',
  phases: [{ title: '토대' }, { title: '채움' }, { title: '검증' }, { title: '수정·마무리' }],
}

// diff 스키마 (Phase 3 검증 에이전트 공통 출력 / Phase 4 F1 입력) — 고정 8필드
const DIFF_SCHEMA = {
  type: 'object', required: ['diffs'],
  properties: { diffs: { type: 'array', items: {
    type: 'object',
    required: ['cardId', 'cardType', 'scope', 'field', 'current', 'expected', 'howToFix', 'severity'],
    properties: {
      cardId: { type: 'string' }, cardType: { type: 'string' }, scope: { type: 'string' },
      field: { type: 'string' }, current: { type: 'string' }, expected: { type: 'string' },
      howToFix: { type: 'string' }, severity: { type: 'string', enum: ['high', 'medium', 'low'] },
    },
  } } },
}

// ── 입력 ──────────────────────────────────────────────────────────────
// args = { editorId, figmaFileKey, figmaNodeId, mode }
//   mode: 'full'  = 생성(S)→검증(V)→수정(F1)→마무리(F2)   (기본)
//         'fix'   = 검증(V)→수정(F1)  (이미 채워진 에디터 교정)
//         'verify'= 검증(V)만 산출     (5025 같은 기존 에디터 QA — 읽기 위주)
// ⚠️ 실행 전 세션 리로드 필요: 신규 에이전트(S1~S6·V2~V5·F2)는 세션 시작 시 로드된
//    레지스트리에만 잡힘 → 파일 생성 직후 같은 세션에선 agentType 미해결. 리로드 후 실행.
const a = args || {}
const editorId = a.editorId
const figmaNodeId = a.figmaNodeId
const figmaFileKey = a.figmaFileKey
const mode = a.mode || 'full'
if (!editorId || !figmaNodeId) {
  log('❌ editorId·figmaNodeId 필수 (figmaFileKey 권장). 예: {editorId:"5025", figmaFileKey:"2CX...", figmaNodeId:"8-3425", mode:"verify"}')
  return { error: 'missing-args' }
}
const figmaRef = figmaFileKey ? `${figmaFileKey} node ${figmaNodeId}` : figmaNodeId
let reservation = null

// ── Phase 1·2: 토대 + 채움 (full 모드만) ──────────────────────────────
if (mode === 'full') {
  phase('토대')
  await agent(`editor ${editorId}, figma ${figmaRef}: 페이지 테마 3색·서체·버튼모양·페이지배경·제목·스크롤애니메이션·멀티페이지 설정.`,
    { agentType: 'cdbd-edit-s1-foundation', label: 'S1 토대', phase: '토대' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 카드 매니페스트대로 15종 카드 추가·순서·상하고정·라벨(목적 이름).`,
    { agentType: 'cdbd-edit-s2-cards', label: 'S2 구성', phase: '토대' })

  phase('채움')
  await agent(`editor ${editorId}, figma ${figmaRef}: 모든 텍스트 필드+버튼 텍스트+줄바꿈 채움(디자인은 V/F).`,
    { agentType: 'cdbd-edit-s3-text', label: 'S3 텍스트', phase: '채움' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 모든 이미지 슬롯 업로드·적용(순서). 모양·크기는 V2.`,
    { agentType: 'cdbd-edit-s4-image', label: 'S4 이미지', phase: '채움' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 링크 6종·위치 지오코딩·Q&A폼·유튜브·SNS.`,
    { agentType: 'cdbd-edit-s5-link', label: 'S5 링크', phase: '채움' })
  reservation = await agent(`editor ${editorId}: 예약 날짜·시간·정원·방문체크(필수). 크레딧 부족 시 부분완료 리포트(중단 ❌).`,
    { agentType: 'cdbd-edit-s6-reservation', label: 'S6 예약', phase: '채움' })
}

// ── 스냅샷 1회 (직렬) — CdBd dumpState + Figma spec을 파일로 병합 ──────
phase('검증')
const snapPath = `/tmp/cdbd-snap-${editorId}.json`
await agent(
  `editor ${editorId}에 skill cdbd-card-automation의 card-driver를 주입 후 window.__cdbd.dumpState()로 전체 블록을 얻고, figma ${figmaRef}의 get_design_context(+get_metadata)로 텍스트·비텍스트 디자인 스펙을 얻어, blockIndex(CdBd blocks와 0-based 1:1)별로 정렬해 ${snapPath}에 저장하라. 형식: {"editorId","cdbd":{blocks,theme},"figmaText":{expected:[{blockIndex,fontFamily,fontSize,bold,color,lineHeight,textAlign}...]},"figmaNonText":{byBlock:[{blockIndex,image,divider,button,card,layout,map}...]}}. 폰트는 CdBd 표기(gounBatang/gounDotum 등)로 변환. 파일 경로만 반환.`,
  { agentType: 'general-purpose', label: '스냅샷', phase: '검증' })

// ── Phase 3: 검증 (V1~V5 병렬, 스냅샷 파일만 — 브라우저·Figma 라이브 금지) ──
const V = ['v1-textdesign', 'v2-imageshape', 'v3-button-divider', 'v4-layout', 'v5-carddesign']
const reviews = await parallel(V.map(v => () =>
  agent(`스냅샷 파일 ${snapPath} 만 읽어 ${v} 스코프 diff를 스키마대로 산출. 브라우저·Figma 라이브 접근 금지. cardId=block.id.`,
    { agentType: `cdbd-edit-${v}`, schema: DIFF_SCHEMA, label: v, phase: '검증' })))
let diffs = reviews.filter(Boolean).flatMap(r => (r && r.diffs) || [])

// 디둡: 같은 cardId+field 중복 제거 (예: V3↔V5 버튼 borderRadius). high severity 우선 유지.
const rank = { high: 0, medium: 1, low: 2 }
const best = {}
for (const d of diffs) {
  const k = d.cardId + '|' + d.field
  if (!best[k] || rank[d.severity] < rank[best[k].severity]) best[k] = d
}
diffs = Object.keys(best).map(k => best[k])
log(`검증 완료: ${diffs.length} diff (디둡 후) · 심각도 high=${diffs.filter(d => d.severity === 'high').length}`)

if (mode === 'verify') return { mode, editorId, diffCount: diffs.length, diffs }

// ── Phase 4: 수정(F1) + 마무리(F2) ────────────────────────────────────
phase('수정·마무리')
// 카드ID로 그룹핑 (F1은 참조 mutate + reorder-commit이라 카드별 그룹이 자연스러움)
const byCard = {}
for (const d of diffs) { (byCard[d.cardId] || (byCard[d.cardId] = [])).push(d) }
const fixed = []
for (const cardId of Object.keys(byCard)) {
  const r = await agent(
    `editor ${editorId}, 카드 ${cardId}의 diff를 적용하라(참조 mutate → reorder-commit 영속화). diff: ${JSON.stringify(byCard[cardId])}`,
    { agentType: 'cdbd-edit-f1-fix', label: `F1 ${cardId.slice(0, 6)}`, phase: '수정·마무리' })
  if (r) fixed.push(r)
}

let screenshots = null
if (mode === 'full') {
  screenshots = await agent(
    `editor ${editorId} 마무리: URL 정보(제목·설명) 설정·OG 이미지 수동 준비 안내·모바일 프리뷰 캡처(멀티=전 페이지)·재스냅샷으로 잔여 diff 확인.`,
    { agentType: 'cdbd-edit-f2-finalize', label: 'F2 마무리', phase: '수정·마무리' })
}

return {
  mode, editorId,
  diffCount: diffs.length,
  fixedCards: Object.keys(byCard).length,
  reservation, screenshots,
  location: `https://www.cdbd.in/editor/${editorId}`,
}
