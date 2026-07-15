export const meta = {
  name: 'cdbd-editor-pipeline',
  description: 'CdBd 4단계: Figma 시안을 CdBd 에디터에 생성→검증(교차확인+통일성 C1)→수정(F→V 재검증 루프)→마무리 (14 스코프)',
  phases: [{ title: '토대' }, { title: '채움' }, { title: '검증' }, { title: '수정·마무리' }],
}

// diff 스키마 (검증 에이전트 공통 출력 / F1 입력) — 고정 8필드
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
//   mode: 'full'  = 생성(S)→검증(V+C1)→수정(F1 루프)→마무리(F2)   (기본)
//         'fix'   = 검증→수정 루프  (이미 채워진 에디터 교정)
//         'verify'= 검증만 산출     (기존 에디터 QA — 읽기 위주)
// ⚠️ 실행 전 세션 리로드 필요: 에이전트(editor-*)는 세션 시작 시 로드된 레지스트리에만
//    잡힘 → 파일 리네임/생성 직후 같은 세션에선 agentType 미해결. 리로드 후 실행.
let a = args || {}
if (typeof a === 'string') { try { a = JSON.parse(a) } catch (e) { a = {} } }
const editorId = a.editorId
const figmaNodeId = a.figmaNodeId
const figmaFileKey = a.figmaFileKey
const mode = a.mode || 'full'
const MAX_REVERIFY = 2   // F 뒤 V 재검증 루프 최대 횟수 (daily 매니저 retry≤2와 정렬)
if (!editorId || !figmaNodeId) {
  log('❌ editorId·figmaNodeId 필수. 예: {editorId:"5025", figmaFileKey:"2CX...", figmaNodeId:"8-3425", mode:"verify"}')
  return { error: 'missing-args' }
}
const figmaRef = figmaFileKey ? `${figmaFileKey} node ${figmaNodeId}` : figmaNodeId
let reservation = null

// 검수자 6 = V1~V5(카드×속성) + C1(전역 통일성). 전부 읽기 전용 → 병렬 안전.
const CHECKERS = [
  { at: 'editor-v1-textdesign', name: 'V1 텍스트' },
  { at: 'editor-v2-imageshape', name: 'V2 이미지·모양' },
  { at: 'editor-v3-button-divider', name: 'V3 버튼·구분선' },
  { at: 'editor-v4-layout', name: 'V4 레이아웃' },
  { at: 'editor-v5-carddesign', name: 'V5 카드디자인' },
  { at: 'editor-c1-consistency', name: 'C1 통일성' },
]

// 스냅샷 1회 (직렬) — CdBd dumpState + Figma spec 병합 → 파일
async function snapshot(tag, phaseTag) {
  const p = `/tmp/cdbd-snap-${editorId}${tag ? '-' + tag : ''}.json`
  await agent(
    `editor ${editorId}에 skill cdbd-card-automation의 card-driver를 주입 후 window.__cdbd.dumpState()로 전체 블록을 얻고, figma ${figmaRef}의 get_design_context(+get_metadata)로 텍스트·비텍스트 디자인 스펙을 얻어, blockIndex(CdBd blocks와 0-based 1:1)별로 정렬해 ${p}에 저장하라. 형식: {"editorId","cdbd":{blocks,theme},"figmaText":{expected:[{blockIndex,fontFamily,fontSize,bold,color,lineHeight,textAlign}...]},"figmaNonText":{byBlock:[{blockIndex,image,divider,button,card,layout,map}...]}}. 폰트는 CdBd 표기(gounBatang/gounDotum 등)로 변환. 파일 경로만 반환.`,
    { agentType: 'general-purpose', label: `스냅샷${tag ? ' ' + tag : ''}`, phase: phaseTag || '검증' })
  return p
}

// 검증 = V1~V5 + C1 병렬(스냅샷 파일만) → 디둡 → {diffs, verifierOK, expected}
async function verify(snapPath, phaseTag) {
  const reviews = await parallel(CHECKERS.map(c => () =>
    agent(`스냅샷 파일 ${snapPath} 만 읽어 ${c.name} 스코프 diff를 스키마대로 산출. 브라우저·Figma 라이브 접근 금지. cardId=block.id.`,
      { agentType: c.at, schema: DIFF_SCHEMA, label: c.name, phase: phaseTag || '검증' })))
  const verifierOK = reviews.filter(Boolean).length
  let ds = reviews.filter(Boolean).flatMap(r => (r && r.diffs) || [])
  // 디둡: 같은 cardId+field 중복 제거 (예: V3↔V5 버튼 borderRadius). high severity 우선 유지.
  const rank = { high: 0, medium: 1, low: 2 }
  const best = {}
  for (const d of ds) {
    const k = d.cardId + '|' + d.field
    if (!best[k] || rank[d.severity] < rank[best[k].severity]) best[k] = d
  }
  return { diffs: Object.keys(best).map(k => best[k]), verifierOK, expected: CHECKERS.length }
}

// ── Phase 1·2: 토대 + 채움 (full 모드만) ──────────────────────────────
if (mode === 'full') {
  phase('토대')
  await agent(`editor ${editorId}, figma ${figmaRef}: 페이지 테마 3색·서체·버튼모양·페이지배경·제목·스크롤애니메이션·멀티페이지 설정.`,
    { agentType: 'editor-s1-foundation', label: 'S1 토대', phase: '토대' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 카드 매니페스트대로 15종 카드 추가·순서·상하고정·라벨(목적 이름).`,
    { agentType: 'editor-s2-cards', label: 'S2 구성', phase: '토대' })

  phase('채움')
  await agent(`editor ${editorId}, figma ${figmaRef}: 모든 텍스트 필드+버튼 텍스트+줄바꿈 채움(디자인은 V/F).`,
    { agentType: 'editor-s3-text', label: 'S3 텍스트', phase: '채움' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 모든 이미지 슬롯 업로드·적용(순서). 모양·크기는 V2.`,
    { agentType: 'editor-s4-image', label: 'S4 이미지', phase: '채움' })
  await agent(`editor ${editorId}, figma ${figmaRef}: 링크 6종·위치 지오코딩·Q&A폼·유튜브·SNS.`,
    { agentType: 'editor-s5-link', label: 'S5 링크', phase: '채움' })
  reservation = await agent(`editor ${editorId}: 예약 날짜·시간·정원·방문체크(필수). 크레딧 부족 시 부분완료 리포트(중단 ❌).`,
    { agentType: 'editor-s6-reservation', label: 'S6 예약', phase: '채움' })
}

// ── Phase 3: 검증 (스냅샷 → V+C1 병렬 → 교차확인 → 거짓클린 게이트) ────
phase('검증')
let snapPath = await snapshot('', '검증')
const v0 = await verify(snapPath, '검증')
let diffs = v0.diffs
let unverified = v0.verifierOK < v0.expected
if (unverified) log(`⚠️ 검수자 ${v0.verifierOK}/${v0.expected}만 성공 — 거짓클린 방지: '미검증' 표시(diff 0이라도 clean 단정 ❌)`)

// 교차확인(반대 눈): 각 diff가 실제 불일치인지 / CdBd-legal 오탐인지 재판정 → 살아남은 것만 F로
if (diffs.length) {
  const conf = await agent(
    `스냅샷 ${snapPath}와 아래 diff 목록을 '반대 눈'으로 검토하라. 각 diff가 (a) 실제 불일치가 맞는지, (b) CdBd-legal 허용오차(padding±2·radius±1·모서리 3옵션·비율 2종·theme 상속) 안이라 오탐인지 판정. 진짜만 남긴 diffs를 스키마대로 반환(오탐은 제외). 브라우저·Figma 라이브 금지. diff: ${JSON.stringify(diffs)}`,
    { agentType: 'general-purpose', schema: DIFF_SCHEMA, label: '교차확인', phase: '검증' })
  if (conf && Array.isArray(conf.diffs)) {
    const before = diffs.length
    diffs = conf.diffs
    log(`교차확인: ${before} → ${diffs.length} (오탐 ${Math.max(0, before - diffs.length)}건 제거)`)
  }
}
log(`검증 완료: ${diffs.length} diff · high=${diffs.filter(d => d.severity === 'high').length}${unverified ? ' · ⚠️미검증' : ''}`)

if (mode === 'verify') return { mode, editorId, diffCount: diffs.length, diffs, unverified, verifierOK: v0.verifierOK, expected: v0.expected }

// ── Phase 4: 수정(F1 카드별) + F→V 재검증 루프(≤MAX_REVERIFY) + 마무리(F2) ──
phase('수정·마무리')
let remaining = diffs
const rounds = []
let round = 0
while (remaining.length && round < MAX_REVERIFY) {
  round++
  // 카드ID로 그룹핑 → F1 (참조 mutate + reorder-commit로 영속화)
  const byCard = {}
  for (const d of remaining) { (byCard[d.cardId] || (byCard[d.cardId] = [])).push(d) }
  for (const cardId of Object.keys(byCard)) {
    await agent(
      `editor ${editorId}, 카드 ${cardId}의 diff를 적용하라(참조 mutate → reorder-commit 영속화). diff: ${JSON.stringify(byCard[cardId])}`,
      { agentType: 'editor-f1-fix', label: `F1 r${round} ${cardId.slice(0, 6)}`, phase: '수정·마무리' })
  }
  const fixedCards = Object.keys(byCard).length
  // 재검증(독립): F가 고친 뒤 재스냅샷 → V+C1 재실행 (자기 결과를 자기가 판단하지 않게)
  const rsnap = await snapshot(`r${round}`, '수정·마무리')
  const re = await verify(rsnap, '수정·마무리')
  rounds.push({ round, fixedCards, remaining: re.diffs.length, verifierOK: re.verifierOK })
  if (re.verifierOK < re.expected) {
    log(`⚠️ 재검증 r${round}: 검수자 ${re.verifierOK}/${re.expected} — 미검증(루프 중단, 리포트 표기)`)
    unverified = true
    remaining = re.diffs
    break
  }
  remaining = re.diffs
  log(`재검증 r${round}: 남은 diff ${remaining.length}${remaining.length ? '' : ' — ✅ 정합'}`)
  if (!remaining.length) break
}
if (remaining.length) log(`⚠️ 재검증 ${round}회 후에도 ${remaining.length} diff 잔존 — 리포트 기재(수동 확인 권장)`)

let screenshots = null
if (mode === 'full') {
  screenshots = await agent(
    `editor ${editorId} 마무리: URL 정보(제목·설명) 설정·OG 이미지 수동 준비 안내·모바일 프리뷰 캡처(멀티=전 페이지)·재스냅샷으로 잔여 diff 확인.`,
    { agentType: 'editor-f2-finalize', label: 'F2 마무리', phase: '수정·마무리' })
}

return {
  mode, editorId,
  initialDiffs: diffs.length,
  remainingDiffs: remaining.length,
  reverifyRounds: rounds,
  unverified,
  reservation, screenshots,
  location: `https://www.cdbd.in/editor/${editorId}`,
}
