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

// TODO(Task 15): 오케스트레이션 본문 — 토대→채움→스냅샷→검증(병렬)→카드별 그룹핑→수정·마무리
log('cdbd-editor-pipeline: 스텁 (Task 15에서 오케스트레이션 완성). DIFF_SCHEMA 필드=' + Object.keys(DIFF_SCHEMA.properties.diffs.items.properties).join(','))
return { stub: true }
