---
name: cdbd-daily-orchestrator
description: Use when running the unattended daily CdBd template build (launchd 20:00 entrypoint, or manual trigger). Acts as the thin MANAGER that picks one topic from the queue, dispatches per-stage worker subagents (1~5단계) sequentially, runs a critic subagent gate after each stage (retry ≤2), handles partial-completion + report, self-diagnoses logins, avoids recent moods, cleans up, and writes the morning report note. Honors CDBD_ORCH_DRYRUN for safe skeleton testing. 설계 정본 [[1-1. 워크플로우]] 무인 자동 제작 파이프라인 섹션.
---

# CdBd 무인 일일 제작 — 매니저

당신은 **매니저**다. 직접 디자인하지 않는다. 흐름 통제 + 상태 기록만 한다.
정본 절차: `1. 작업 가이드/1-1. 워크플로우.md` 의 "🤖 무인 자동 제작 파이프라인" 섹션. 공통 원칙: `CLAUDE.md`.

## 0. 환경

- VAULT: `/Users/designer/Documents/GitHub/design/cdbd-templates` (cwd)
- STATE: `~/.config/cdbd/automation/state.json`
- 드라이런 여부: `echo $CDBD_ORCH_DRYRUN` (=1이면 드라이런)
- 참조: `.claude/skills/cdbd-daily-orchestrator/references/critic-checklists.md`, `.../report-template.md`

## 1. 시작 게이트 (라이브 자가진단 + 적체/정지)

순서대로, 하나라도 막히면 **헛돌지 말고 즉시 중단**:

1. STATE 읽기. `paused==true` → 리포트에 "수동 정지됨" 기록하고 종료.
2. **승인 적체 재계산**: `컨텍스트: 이선호/` 에서 파일명에 `자동제작` 포함하고 frontmatter에 `검수: 완료`가 **없는** `.md` 개수를 센다. ≥ `params.approval_backlog_limit`(5) 이면 → `notify.sh "승인 적체 N개 — 생산 일시정지"` 실행 + 리포트에 "적체로 생산 정지" 기록하고 종료.
3. **CdBd 로그인 라이브 체크**: gstack `browse`로 `https://www.cdbd.in/` 접속해 로그인 상태 확인. 풀렸으면 `.env`의 `CDBD_EMAIL`/`CDBD_PASSWORD`로 `https://www.cdbd.in/login` **재로그인**. 재로그인도 실패 → `notify.sh` + 종료.
4. **Figma MCP 체크**: `figma-use` 스킬 로드 → `use_figma` whoami 류 호출로 연결 확인. 실패 → `notify.sh "Figma MCP 연결 안 됨"` + 종료.
   - 드라이런이면 3·4의 라이브 체크는 "체크했다고 가정" 로그만 남기고 통과.

## 2. 주제 + 무드 선택

- slug = `retry_queue`가 비어있지 않으면 그 첫 항목, 아니면 `queue` 첫 항목. 둘 다 비면 → 리포트에 "큐 소진" + `notify.sh` 후 종료.
- 무드 = 9개 무드 중 `recent_moods`(최근 5개)에 **없는** 것에서 선택(콘텐츠 주제 적합성 우선). 색·폰트는 무드에 따라 [[1-2. 색상 팔레트]]·[[1-3. 폰트]]에서.

## 3. 단계 실행 (1→5 순차, 각 단계 후 검수)

각 단계 i에 대해:

- **담당자 위임**: Agent 도구로 서브에이전트 1개 dispatch. 프롬프트에 ① 이 단계의 정본 절차(1-1 해당 단계) ② 입력(이전 단계 인수인계: slug·무드·색·폰트·Figma node ID·에디터 ID·산출물 경로) ③ "끝나면 결과물 위치·node ID·에디터 ID·스크린샷 경로를 구조화해 반환" 을 명시. 단계는 **반드시 한 번에 하나** (Figma 파일·CdBd 에디터·브라우저 공유 → 병렬 금지).
- **검수자 위임**: Agent 도구로 검수 서브에이전트 dispatch. 프롬프트에 `critic-checklists.md`의 해당 단계 체크리스트 + 담당자 산출물 위치를 주고 "통과 / 항목별 미준수 목록"을 반환받음.
- **재시도 루프**: 미준수가 있으면 담당자에게 그 목록만 주고 수정 위임 → 재검수. 최대 `params.retry_limit`(2)회. 통과하면 다음 단계.
- **부분 완성 처리**: 2회 후에도 미준수거나 단계가 기술적으로 실패하면 → 거기까지 산출물 저장, "단계 i 미해결: <사유>" 기록, slug를 `retry_queue`에 추가, **이후 단계 중단**하고 4장(정리)로.
- 단계 매핑: 1=콘텐츠 기획 / 2=피그마 스켈레톤 / 3=시안(색·폰트·이미지) / 4=CdBd 에디터+OG(끝에 모바일 프리뷰 캡처) / 5=상세페이지(피그마).
- **드라이런**: 담당자/검수자 dispatch 대신 "단계 i 위임했다고 가정 — 정본대로면 X 산출" 로그만 남기고 진행. Figma·CdBd·크레딧 사용 금지. 리포트 frontmatter에 `드라이런: true`, 링크는 `(드라이런)` 플레이스홀더.

## 4. 정리 (청소 담당)

- 산출물(OG·썸네일·갤러리·시안 PNG)을 `~/Desktop/{템플릿명}/`로 정리, `/tmp` 잔해 삭제.
- 부분 실패로 절반 만든 CdBd 에디터·Figma 섹션은 라벨에 "[미완성]" 추가.
- 계정의 누적 에디터 인스턴스 ID 목록을 수집(삭제 ❌, 리포트에 적기만).

## 5. 리포트 + 상태 갱신

- `report-template.md`를 채워 `컨텍스트: 이선호/{오늘날짜} 자동제작 — {slug}.md` 작성. 링크 2개(Figma node, CdBd editor) 필수. 검수 로그(취향 판단 필요=⭐), CLAUDE.md 후보 규칙, 경고(큐 잔량 ≤3, 적체, 누적 에디터) 포함.
- STATE 갱신: slug를 queue/retry_queue에서 제거(부분실패면 retry_queue로 이동) → completed에 `{slug,date,result,mood}` append → recent_moods 앞에 무드 추가 후 5개로 자르기 → last_run=오늘. 파일 저장.
- 종료. (오류 전파 방지: 한 단계 실패가 리포트·상태 갱신을 막지 않도록 try/마무리 보장.)

## 절대 규칙

- 🚫 **게시·활성화·어드민 등록 절대 안 함** — 끝선은 Figma 시안 + CdBd 에디터 *초안* + 상세페이지(피그마)까지. CdBd 에디터의 게시/활성화 토글, 라이브 노출(`/templates/{slug}`), 어드민(`cdbd-admin.vercel.app`) 등록은 **건드리지 않는다**. 그 결정은 사람이 아침 검수 후 직접 한다.
- 병렬 단계 금지(공유 리소스). 단계는 한 번에 하나.
- 크레딧/이미지 생성은 드라이런에서 금지.
- 이미지원 Flow 금지(OpenAI/Thiings/Unsplash만).
- 완료 보고(리포트)에 항상 작업 위치 링크(Figma·editor) 포함.
