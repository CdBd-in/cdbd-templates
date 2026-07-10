# CdBd 무인 일일 템플릿 제작 오케스트레이터 — 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 매일 밤 8시 맥에서 무인으로 신규 CdBd 템플릿 1개를 1~5단계(어드민 등록 제외)까지 제작하고 아침 리포트 노트를 남기는 오케스트레이터를 구축한다.

**Architecture:** 얇은 매니저(오케스트레이터 스킬) + 단계별 담당자(서브에이전트) + 검수자(서브에이전트) 구조. `launchd`가 20:00에 `run-daily.sh`를 실행 → 자가진단 통과 시 `caffeinate`로 맥을 깨운 채 `claude -p` 헤드리스로 매니저를 깨움 → 매니저가 `cdbd-daily-orchestrator` 스킬을 따라 단계별 서브에이전트를 순차 위임·검수하고 상태/리포트를 기록. 모든 정본 파일은 vault 스킬 폴더에 버전관리하고 `install.sh`가 `~/.config`·`~/Library/LaunchAgents`로 배포한다.

**Tech Stack:** zsh 스크립트, macOS `launchd`/`caffeinate`/`osascript`, `claude` 헤드리스 CLI(`/Users/designer/.local/bin/claude`), Claude Agent/Skill 도구, 기존 스킬(`cdbd-card-automation`, `figma-use`), `jq`(JSON 검증).

## Global Constraints

- 설계 정본: [[1-1. 워크플로우]] `## 🤖 무인 자동 제작 파이프라인 (매일 1개)` 섹션. 모든 동작은 그 설계를 따른다.
- 공통 원칙·환경·카드 정책: [[CLAUDE.md]] (재기재 ❌, 참조).
- vault 절대경로: `/Users/designer/Documents/GitHub/design/cdbd-templates`
- claude 바이너리: `/Users/designer/.local/bin/claude`
- 자격증명: CdBd 로그인 = vault `.env`(`CDBD_EMAIL`/`CDBD_PASSWORD`) · OpenAI = `~/.config/cdbd/credentials.json`
- 확정 파라미터값(절대 변경 금지, verbatim): 재시도 횟수 **2**(단계당 총 3회) · 승인 적체 한계 **5** · 큐 잔량 경고 임계 **3** · 최근 무드 회피 윈도 **5**
- 이미지원: OpenAI gpt-image-1 / Thiings 3D / Unsplash. 🚫 **Flow 제외**.
- 어드민 등록(6단계)은 **보류** — 파이프라인은 1~5단계까지.
- 리포트 노트 위치: `컨텍스트: 이선호/YYYY-MM-DD 자동제작 — {slug}.md`
- 산출물 폴더: `~/Desktop/{템플릿명}/` · 작업 로그: `~/.config/cdbd/automation/logs/`
- 정본 파일은 vault `.claude/skills/cdbd-daily-orchestrator/`에 두고 vault 자동백업으로 버전관리. `~/.config`·`LaunchAgents`의 사본은 `install.sh`로 재배포 가능.

---

## File Structure

vault 내 정본 (버전관리):
```
.claude/skills/cdbd-daily-orchestrator/
  SKILL.md                       # 매니저 흐름·역할·위임·드라이런 (Task 3)
  references/
    critic-checklists.md         # 단계별 검수 체크리스트 (Task 4)
    report-template.md           # 아침 리포트 템플릿 (Task 4)
    state-schema.md              # state.json 스키마 문서 (Task 1)
  runtime/                       # install.sh가 ~/.config 등으로 배포
    state.seed.json              # 초기 상태(큐 시드) (Task 1)
    preflight.sh                 # 저비용 자가진단 (Task 2)
    notify.sh                    # 맥 알림(하드스톱) (Task 2)
    run-daily.sh                 # launchd 진입점 (Task 5)
    in.cdbd.daily-template.plist # launchd 예약표 (Task 6)
  install.sh                     # 배포기 (Task 6)
```

배포 대상 (재생성 가능, 버전관리 ❌):
```
~/.config/cdbd/automation/{state.json,preflight.sh,notify.sh,run-daily.sh,logs/}
~/Library/LaunchAgents/in.cdbd.daily-template.plist
```

---

## Task 1: 상태 파일 스키마 + 큐 시드

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json`
- Create: `.claude/skills/cdbd-daily-orchestrator/references/state-schema.md`

**Interfaces:**
- Produces: `state.json` 구조 — 키 `queue`(string[]), `retry_queue`(string[]), `recent_moods`(string[]), `completed`({slug,date,result,mood}[]), `params`({retry_limit:2, approval_backlog_limit:5, queue_low_threshold:3, recent_moods_window:5}), `last_run`(string|null), `paused`(bool). 이후 모든 Task가 이 키 이름을 그대로 사용.

- [ ] **Step 1: 큐 시드 파일 작성**

`runtime/state.seed.json` (백로그는 [[3-1. 신규 템플릿 18건 정리]]의 미완료 slug):

```json
{
  "queue": [
    "vip-dinner", "church-rsvp", "omakase-reserve", "event-ticket",
    "beauty-catalog", "interior-portfolio", "freelancer-card",
    "coach-card", "startup-deck", "trade-show", "agency-card",
    "medical-slot", "popup-timed"
  ],
  "retry_queue": [],
  "recent_moods": [],
  "completed": [],
  "params": {
    "retry_limit": 2,
    "approval_backlog_limit": 5,
    "queue_low_threshold": 3,
    "recent_moods_window": 5
  },
  "last_run": null,
  "paused": false
}
```

- [ ] **Step 2: 스키마 문서 작성**

`references/state-schema.md`:

```markdown
# state.json 스키마

배포 위치: `~/.config/cdbd/automation/state.json` (정본 시드: 스킬 `runtime/state.seed.json`)

| 키 | 타입 | 의미 |
|---|---|---|
| `queue` | string[] | 아직 제작 안 한 주제 slug, 앞에서부터 소비 |
| `retry_queue` | string[] | 실패해 "재시도 대기"인 slug. queue보다 우선 소비 |
| `recent_moods` | string[] | 최근 사용 무드(최대 recent_moods_window개). 매니저가 회피 |
| `completed` | object[] | `{slug,date,result,mood}` 누적 기록. result∈{완성,부분,실패} |
| `params.retry_limit` | int=2 | 단계당 재시도 횟수(총 시도 = +1) |
| `params.approval_backlog_limit` | int=5 | 미검수 리포트 N개 이상이면 생산 일시정지 |
| `params.queue_low_threshold` | int=3 | queue 길이 ≤ N이면 잔량 경고 |
| `params.recent_moods_window` | int=5 | recent_moods 최대 길이 |
| `last_run` | string\|null | 마지막 실행 ISO 날짜 |
| `paused` | bool | true면 매니저가 즉시 중단(수동 정지) |

매니저는 매 실행 종료 시: 선택한 slug를 queue/retry_queue에서 제거 → 결과를 completed에 append → 무드를 recent_moods 앞에 추가(window 초과분 잘라냄) → last_run 갱신.
승인 적체(approval_backlog)는 저장하지 않고 **매 실행 시작 시 재계산**(Task 3): `컨텍스트: 이선호/` 의 `자동제작` 리포트 중 frontmatter에 `검수: 완료`가 없는 노트 수.
```

- [ ] **Step 3: JSON 유효성 검증**

Run: `jq -e '.queue|length>0 and .params.retry_limit==2 and .params.approval_backlog_limit==5' ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json"`
Expected: 출력 `true`, 종료코드 0.

- [ ] **Step 4: 커밋** (vault 자동백업이 처리하나 명시적으로)

```bash
git add ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" ".claude/skills/cdbd-daily-orchestrator/references/state-schema.md"
git commit -m "feat(orchestrator): state 스키마 + 큐 시드"
```

---

## Task 2: 자가진단 + 맥 알림 스크립트

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh`
- Create: `.claude/skills/cdbd-daily-orchestrator/runtime/notify.sh`

**Interfaces:**
- Produces: `preflight.sh` — 종료코드 0=통과, 1=실패(저비용 체크만: creds 파일·.env·네트워크). `notify.sh "<메시지>"` — macOS 알림 1개 표시.
- 라이브 체크(CdBd 로그인 살아있나·Figma MCP 연결)는 매니저 에이전트(Task 3)가 수행 — 셸로는 불가.

- [ ] **Step 1: notify.sh 작성**

```sh
#!/bin/zsh
# 사용법: notify.sh "메시지"
MSG="${1:-CdBd 자동제작 알림}"
/usr/bin/osascript -e "display notification \"${MSG}\" with title \"CdBd 자동제작\" sound name \"Basso\""
```

- [ ] **Step 2: preflight.sh 작성**

```sh
#!/bin/zsh
# 저비용 자가진단. 0=통과, 1=실패. 라이브 로그인/ MCP 체크는 매니저가 함.
set -u
VAULT="/Users/designer/Documents/GitHub/design/cdbd-templates"
fail() { echo "PREFLIGHT FAIL: $1"; exit 1; }

[ -f "$HOME/.config/cdbd/credentials.json" ] || fail "OpenAI creds 없음"
[ -f "$VAULT/.env" ] || fail ".env 없음"
grep -q "CDBD_EMAIL" "$VAULT/.env" || fail ".env에 CDBD_EMAIL 없음"
grep -q "CDBD_PASSWORD" "$VAULT/.env" || fail ".env에 CDBD_PASSWORD 없음"
/usr/bin/curl -sf -o /dev/null --max-time 15 "https://www.cdbd.in/login" || fail "cdbd.in 도달 불가(네트워크)"

echo "PREFLIGHT OK"
exit 0
```

- [ ] **Step 3: 실행 권한 부여 + 통과 케이스 검증**

Run:
```bash
chmod +x ".claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh" ".claude/skills/cdbd-daily-orchestrator/runtime/notify.sh"
".claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh"; echo "rc=$?"
```
Expected: `PREFLIGHT OK` 출력 + `rc=0`.

- [ ] **Step 4: 실패 케이스 검증 (네트워크 무관, creds 경로 가짜로)**

Run:
```bash
HOME=/tmp/nope ".claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh"; echo "rc=$?"
```
Expected: `PREFLIGHT FAIL: OpenAI creds 없음` + `rc=1`.

- [ ] **Step 5: 알림 동작 확인 (수동, 화면에 알림 1개)**

Run: `".claude/skills/cdbd-daily-orchestrator/runtime/notify.sh" "테스트 알림"`
Expected: 우상단에 "CdBd 자동제작 — 테스트 알림" 알림 표시.

- [ ] **Step 6: 커밋**

```bash
git add ".claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh" ".claude/skills/cdbd-daily-orchestrator/runtime/notify.sh"
git commit -m "feat(orchestrator): preflight 자가진단 + 맥 알림"
```

---

## Task 3: 오케스트레이터 스킬 (매니저 본체 + 드라이런)

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/SKILL.md`

**Interfaces:**
- Consumes: `state.json`(Task 1), `preflight.sh`/`notify.sh`(Task 2), `critic-checklists.md`/`report-template.md`(Task 4 — Task 3에서 경로만 참조, Task 4에서 채움).
- Produces: 스킬 호출 시 매니저가 따르는 절차. 드라이런 모드(`CDBD_ORCH_DRYRUN=1`)에서는 무거운 단계 작업을 건너뛰고 골격(상태·큐·무드회피·적체·리포트·정리)만 실행.

- [ ] **Step 1: SKILL.md 작성 (전체 내용)**

```markdown
---
name: cdbd-daily-orchestrator
description: Use when running the unattended daily CdBd template build (launchd 20:00 entrypoint, or manual trigger). Acts as the thin MANAGER that picks one topic from the queue, dispatches per-stage worker subagents (1~5단계) sequentially, runs a critic subagent gate after each stage (retry ≤2), handles partial-completion + report, self-diagnoses logins, avoids recent moods, cleans up, and writes the morning report note. Honors CDBD_ORCH_DRYRUN for safe skeleton testing. 설계 정본: [[1-1. 워크플로우]] 무인 자동 제작 파이프라인 섹션.
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
- **드라이런**: 담당자/검수자 dispatch 대신 "단계 i 위임했다고 가정 — 정본대로면 X 산출" 로그만 남기고 진행. Figma·CdBd·크레딧 사용 금지. 링크는 `(드라이런)` 플레이스홀더.

## 4. 정리 (청소 담당)

- 산출물(OG·썸네일·갤러리·시안 PNG)을 `~/Desktop/{템플릿명}/`로 정리, `/tmp` 잔해 삭제.
- 부분 실패로 절반 만든 CdBd 에디터·Figma 섹션은 라벨에 "[미완성]" 추가.
- 계정의 누적 에디터 인스턴스 ID 목록을 수집(삭제 ❌, 리포트에 적기만).

## 5. 리포트 + 상태 갱신

- `report-template.md`를 채워 `컨텍스트: 이선호/{오늘날짜} 자동제작 — {slug}.md` 작성. 링크 2개(Figma node, CdBd editor) 필수. 검수 로그(취향 판단 필요=⭐), CLAUDE.md 후보 규칙, 경고(큐 잔량 ≤3, 적체, 누적 에디터) 포함.
- STATE 갱신: slug를 queue/retry_queue에서 제거(부분실패면 retry_queue로 이동) → completed에 `{slug,date,result,mood}` append → recent_moods 앞에 무드 추가 후 5개로 자르기 → last_run=오늘. 파일 저장.
- 종료. (오류 전파 방지: 한 단계 실패가 리포트·상태 갱신을 막지 않도록 try/마무리 보장.)

## 절대 규칙

- 병렬 단계 금지(공유 리소스). 단계는 한 번에 하나.
- 크레딧/이미지 생성은 드라이런에서 금지.
- 이미지원 Flow 금지(OpenAI/Thiings/Unsplash만).
- 완료 보고(리포트)에 항상 작업 위치 링크(Figma·editor) 포함.
```

- [ ] **Step 2: 스킬 인식 확인**

Run: `ls ".claude/skills/cdbd-daily-orchestrator/SKILL.md" && head -4 ".claude/skills/cdbd-daily-orchestrator/SKILL.md"`
Expected: 파일 존재 + frontmatter `name: cdbd-daily-orchestrator` 출력.

- [ ] **Step 3: 커밋**

```bash
git add ".claude/skills/cdbd-daily-orchestrator/SKILL.md"
git commit -m "feat(orchestrator): 매니저 스킬(드라이런 포함)"
```

> 참고: 스킬의 실제 드라이런 동작 검증은 Task 5(러너)에서 end-to-end로 수행한다 (스킬 단독 호출은 대화 세션이 필요하므로 Task 5의 헤드리스 드라이런으로 한 번에 확인).

---

## Task 4: 검수 체크리스트 + 리포트 템플릿

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/references/critic-checklists.md`
- Create: `.claude/skills/cdbd-daily-orchestrator/references/report-template.md`

**Interfaces:**
- Consumes: Task 3 SKILL.md가 이 두 파일을 경로로 참조.
- Produces: 단계별 검수 항목(2~5단계) + 리포트 마크다운 골격.

- [ ] **Step 1: critic-checklists.md 작성** (정본: 1-1 검수 기준)

```markdown
# 단계별 검수 체크리스트 (검수자용)

각 항목 통과=✅ / 미준수=항목명 반환. 근거 규칙은 1-1 / CLAUDE.md.

## 2단계 — 와이어프레임 (구조)
- [ ] 텍스트 카드 1개 = 속성 1개 (사이즈·정렬·색·줄간격 섞임 없음)
- [ ] 스켈레톤 고정 스펙: 프로필 텍스트 2개만 / Q&A 제목 중앙+제출버튼 카드 하단 내장 / 위치 안내=지도+주소 한 단위 / 자동 gap(SPACE_BETWEEN 등) 없음
- [ ] 모든 카드 top-level 평탄화, 페이지 gap=0, 외부여백=0(배경·테두리 없는 카드는 단일 padding)
- [ ] 편집 불가 장식(팬텀: 골드라인·점선·노치·형광펜) 없음

## 3단계 — 시안 (색·폰트·이미지)
- [ ] 글자-배경 대비 ≥ 3.6:1
- [ ] 버튼색-배경 대비 ≥ 3.6:1 (버튼 글자=배경색이므로 별도 확인)
- [ ] 무드 1개로 색·폰트 통일 / 한 페이지 폰트 1~2개 / 국문 본문=한글 폰트
- [ ] 보조 텍스트 = {텍스트색}×N% 투명도 (별도 회색 hex ❌)
- [ ] 버튼 텍스트 색 = {배경색}
- [ ] 헤드라인 액센트 = {버튼색}(2색 팔레트면 무드 내 별도 포인트색, 배경 대비 ≥3.6:1)
- [ ] 이미지원 = OpenAI/Thiings/Unsplash (Flow ❌)

## 4단계 — CdBd 에디터 (라이브 ↔ 시안 대조)
- [ ] 텍스트 크기·색·정렬·웨이트·줄간격이 시안 실측과 일치
- [ ] 카드 상하 padding=시안 frame, 외부여백 0, page gap 0
- [ ] 구분선 두께·모양·색 / 프로필 이미지 크기(%) / 갤러리 둥글기·그리드 단수·간격 / 버튼 높이
- [ ] OG 이미지: 로고 타입 기본, 800×400 1배수 JPG, 로고 면적 9~10%
- [ ] 카드 라벨 = 목적·내용 이름(기본 타입명 방치 ❌)

## 5단계 — 상세페이지 (피그마)
- [ ] 기존 섹션 복제 후 내용·이미지만 교체(신규 작성 ❌)
- [ ] "10회 사용 / ★4.9" 배지 삭제
- [ ] 슬롯 전부 채움: 대표이미지·썸네일·카테고리·슬러그·에디터 id·소개(제목·성과·리뷰형 설명·추천타겟)·주요기능 N·모바일 스크린샷
```

- [ ] **Step 2: report-template.md 작성**

```markdown
---
세션: 자동제작
slug: {slug}
무드: {무드}
결과: {완성|부분|실패}
검수:        # 사용자가 검토 후 "완료" 기입 → 적체 카운트에서 빠짐
---

# {날짜} 자동제작 — {slug}

> 결과: {✅완성 | ⚠️부분완성 | ❌실패} — {한 줄 요약}

## 링크 (검수용)
- Figma 시안: {figma url, node-id=...}
- CdBd 에디터: https://www.cdbd.in/editor/{id}
- 모바일 프리뷰: ![[{스크린샷 경로}]]

## 주제
- slug / 무드 / 색(배경·텍스트·버튼 hex) / 폰트

## 검수 로그
- 2단계: {통과 / 잡은 항목 → 수정 결과}  (취향 판단 필요 = ⭐)
- 3단계: ...
- 4단계: ...
- 5단계: ...

## CLAUDE.md 후보 규칙 (사용자 승격 결정)
- {새로 발견한 실수 유형, 없으면 "없음"}

## 경고
- 큐 잔량: {N}건 {≤3이면 "⚠️ 곧 소진"}
- 승인 적체: {N}건
- 누적 에디터 인스턴스: {id 목록}
- 로그인/세션 이슈: {있으면}
```

- [ ] **Step 3: 검증 (파일 존재 + 핵심 항목 포함)**

Run: `grep -c "버튼색-배경 대비" ".claude/skills/cdbd-daily-orchestrator/references/critic-checklists.md" && grep -c "검수:" ".claude/skills/cdbd-daily-orchestrator/references/report-template.md"`
Expected: 각각 `1` 출력 (버튼대비 항목·검수 frontmatter 키 존재).

- [ ] **Step 4: 커밋**

```bash
git add ".claude/skills/cdbd-daily-orchestrator/references/"
git commit -m "feat(orchestrator): 검수 체크리스트 + 리포트 템플릿"
```

---

## Task 5: 러너 스크립트 (caffeinate + claude 헤드리스 + 드라이런 E2E)

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/runtime/run-daily.sh`

**Interfaces:**
- Consumes: `preflight.sh`/`notify.sh`(Task 2), `state.json`(Task 1 시드를 Step 1에서 배포), SKILL.md+references(Task 3·4).
- Produces: launchd가 호출할 진입점. preflight 통과 시 맥을 깨운 채 `claude -p`로 매니저를 1회 실행. `CDBD_ORCH_DRYRUN` 전달.

- [ ] **Step 1: run-daily.sh 작성**

```sh
#!/bin/zsh
set -u
DIR="$HOME/.config/cdbd/automation"
VAULT="/Users/designer/Documents/GitHub/design/cdbd-templates"
CLAUDE="/Users/designer/.local/bin/claude"
mkdir -p "$DIR/logs"
LOG="$DIR/logs/$(date +%F).log"
exec >>"$LOG" 2>&1

echo "=== run $(date '+%F %T') dryrun=${CDBD_ORCH_DRYRUN:-0} ==="

if ! "$DIR/preflight.sh"; then
  "$DIR/notify.sh" "자가진단 실패 — 오늘 제작 중단. 로그: $LOG"
  echo "preflight failed; abort"; exit 1
fi

# 작업 동안(최대 3시간) 맥이 잠들지 않게
/usr/bin/caffeinate -i -t 10800 &
CAF=$!

cd "$VAULT" || { echo "vault cd 실패"; kill $CAF 2>/dev/null; exit 1; }
PROMPT="당신은 CdBd 일일 템플릿 매니저입니다. cdbd-daily-orchestrator 스킬을 호출해 오늘의 무인 제작을 1회 실행하세요. 환경변수 CDBD_ORCH_DRYRUN 을 존중하세요(=1이면 드라이런)."

CDBD_ORCH_DRYRUN="${CDBD_ORCH_DRYRUN:-0}" "$CLAUDE" -p "$PROMPT" --dangerously-skip-permissions
RC=$?

kill $CAF 2>/dev/null
echo "=== done rc=$RC $(date '+%F %T') ==="
exit $RC
```

> 보안 주: `--dangerously-skip-permissions`는 무인 실행에 필요(승인 프롬프트 없음). 사용자 본인 맥·이 작업에 한정. 더 좁히려면 추후 `--allowedTools`/settings 허용목록으로 교체 가능(Task 외).

- [ ] **Step 2: 시드 상태 배포(드라이런 검증용) + 실행권한**

Run:
```bash
mkdir -p "$HOME/.config/cdbd/automation/logs"
cp ".claude/skills/cdbd-daily-orchestrator/runtime/preflight.sh" ".claude/skills/cdbd-daily-orchestrator/runtime/notify.sh" ".claude/skills/cdbd-daily-orchestrator/runtime/run-daily.sh" "$HOME/.config/cdbd/automation/"
[ -f "$HOME/.config/cdbd/automation/state.json" ] || cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"
chmod +x "$HOME/.config/cdbd/automation/"*.sh
echo "deployed"
```
Expected: `deployed`.

- [ ] **Step 3: 드라이런 end-to-end 실행**

Run: `CDBD_ORCH_DRYRUN=1 "$HOME/.config/cdbd/automation/run-daily.sh"; echo "rc=$?"`
Expected: `rc=0`. 로그(`~/.config/cdbd/automation/logs/<오늘>.log`)에 `=== run ... dryrun=1 ===` ~ `=== done rc=0 ===`.

- [ ] **Step 4: 드라이런 산출물 검증**

Run:
```bash
ls "컨텍스트: 이선호/"*"자동제작"*.md | tail -1
jq -r '.last_run, (.recent_moods|join(","))' "$HOME/.config/cdbd/automation/state.json"
```
Expected: 오늘 날짜 `자동제작 — {slug}.md` 리포트 노트 1개 존재(링크 자리에 `(드라이런)`), state.json의 `last_run`=오늘·`recent_moods`에 무드 1개. (드라이런이므로 Figma/CdBd 변경·크레딧 사용 없음.)

- [ ] **Step 5: 드라이런 잔해 정리 + 커밋**

Run: `rm -f "컨텍스트: 이선호/"*"자동제작"*"(드라이런)"*.md 2>/dev/null; cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"` (시드로 리셋 — 라이브 전 큐 원복)

```bash
git add ".claude/skills/cdbd-daily-orchestrator/runtime/run-daily.sh"
git commit -m "feat(orchestrator): launchd 러너 + 드라이런 E2E"
```

> 만약 드라이런 리포트에 `(드라이런)` 마커가 없어 Step 5 rm이 안 잡히면, 수동으로 해당 노트를 확인 후 삭제. (드라이런 리포트는 frontmatter `결과` 옆에 `드라이런: true`를 넣도록 SKILL.md Step 1의 드라이런 분기에서 보장 — 검증 시 이 키로 구분.)

---

## Task 6: launchd 예약표 + 설치기

**Files:**
- Create: `.claude/skills/cdbd-daily-orchestrator/runtime/in.cdbd.daily-template.plist`
- Create: `.claude/skills/cdbd-daily-orchestrator/install.sh`

**Interfaces:**
- Consumes: Task 1·2·5의 runtime 파일.
- Produces: 매일 20:00 `run-daily.sh` 실행하는 launchd 에이전트. `install.sh`로 배포·로드.

- [ ] **Step 1: plist 작성**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>in.cdbd.daily-template</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/designer/.config/cdbd/automation/run-daily.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>20</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>/Users/designer/.config/cdbd/automation/logs/launchd.out.log</string>
  <key>StandardErrorPath</key><string>/Users/designer/.config/cdbd/automation/logs/launchd.err.log</string>
</dict>
</plist>
```

> macOS는 20:00에 맥이 잠자기/꺼짐이었으면, 깨어난 직후 놓친 StartCalendarInterval 작업을 1회 실행해 따라잡는다(설계의 "절전이어도 따라잡음").

- [ ] **Step 2: install.sh 작성**

```sh
#!/bin/zsh
set -eu
SRC="$(cd "$(dirname "$0")/runtime" && pwd)"
DEST="$HOME/.config/cdbd/automation"
PLIST="$HOME/Library/LaunchAgents/in.cdbd.daily-template.plist"
mkdir -p "$DEST/logs"

for f in run-daily.sh preflight.sh notify.sh; do
  cp "$SRC/$f" "$DEST/$f"; chmod +x "$DEST/$f"
done
[ -f "$DEST/state.json" ] || cp "$SRC/state.seed.json" "$DEST/state.json"
cp "$SRC/in.cdbd.daily-template.plist" "$PLIST"

launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "installed. 현재 등록 상태:"
launchctl list | grep cdbd || echo "(grep cdbd: 없음 — 확인 필요)"
```

- [ ] **Step 3: 설치 실행 + 등록 확인**

Run: `chmod +x ".claude/skills/cdbd-daily-orchestrator/install.sh" && ".claude/skills/cdbd-daily-orchestrator/install.sh"`
Expected: `installed.` + `launchctl list`에 `in.cdbd.daily-template` 행 출현.

- [ ] **Step 4: launchd가 러너를 부르는지 수동 트리거(드라이런)**

Run:
```bash
launchctl setenv CDBD_ORCH_DRYRUN 1
launchctl start in.cdbd.daily-template
sleep 8
tail -3 "$HOME/.config/cdbd/automation/logs/$(date +%F).log"
launchctl unsetenv CDBD_ORCH_DRYRUN
```
Expected: 로그에 새 `=== run ... dryrun=1 ===` 라인이 추가됨(launchd→run-daily 경로 동작 확인).
> 주: `launchctl setenv`는 launchd 세션 환경에 주입. 라이브 운영에서는 이 변수를 설정하지 않으므로 dryrun=0.

- [ ] **Step 5: 드라이런 잔해 정리 + 커밋**

Run: `rm -f "컨텍스트: 이선호/"*"자동제작"*.md 2>/dev/null; cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"` (라이브 전 리셋; 사람 작성 리포트가 섞였다면 수동 선별)

```bash
git add ".claude/skills/cdbd-daily-orchestrator/runtime/in.cdbd.daily-template.plist" ".claude/skills/cdbd-daily-orchestrator/install.sh"
git commit -m "feat(orchestrator): launchd 예약표 + 설치기"
```

---

## Task 7: 첫 감독 라이브 실행 + 큐/적체 배선 검증 + 게이트

**Files:**
- Modify: `.claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json` (필요 시 큐 미세조정)
- (코드 변경 없이 라이브 1회 실증 + 경고 로직 확인이 주 목적)

**Interfaces:**
- Consumes: Task 1~6 전체.
- Produces: 라이브 1건(실제 Figma·CdBd) 산출 + 경고(큐 잔량·적체) 동작 확인 후 정식 가동.

- [ ] **Step 1: 큐 잔량 경고 동작 확인 (드라이런, 임시 저큐)**

Run:
```bash
jq '.queue=["coach-card","startup-deck"]' ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" > "$HOME/.config/cdbd/automation/state.json"
CDBD_ORCH_DRYRUN=1 "$HOME/.config/cdbd/automation/run-daily.sh"
grep -i "곧 소진\|큐 잔량" "컨텍스트: 이선호/"*"자동제작"*.md | tail -1
```
Expected: 리포트 경고 섹션에 큐 잔량 ≤3 → "⚠️ 곧 소진" 문구 출현. (소비 후 queue 길이 1 ≤ 3)

- [ ] **Step 2: 승인 적체 정지 동작 확인 (드라이런, 가짜 미검수 리포트 5개)**

Run:
```bash
for i in 1 2 3 4 5; do printf -- "---\n세션: 자동제작\n검수:\n---\n적체테스트$i\n" > "컨텍스트: 이선호/2026-01-0$i 자동제작 — test$i.md"; done
cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"
CDBD_ORCH_DRYRUN=1 "$HOME/.config/cdbd/automation/run-daily.sh"
tail -5 "$HOME/.config/cdbd/automation/logs/$(date +%F).log"
```
Expected: 매니저가 적체 ≥5 감지 → "적체로 생산 정지" 로그 + 새 제작 리포트 미생성(또는 정지 리포트만). 검증 후 `rm "컨텍스트: 이선호/2026-01-0"*" 자동제작 — test"*.md`.

- [ ] **Step 3: 라이브 1건 실행 (감독 하, dryrun=0)**

Run: `cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"; "$HOME/.config/cdbd/automation/run-daily.sh"; echo "rc=$?"`
Expected: 실제 1~5단계 진행. 시간이 오래 걸림(수십 분). 종료 후 `rc=0` 또는 부분완성. **실행 중 첫 회는 사람이 로그를 모니터링**.

- [ ] **Step 4: 라이브 산출물 검증**

Run:
```bash
ls "컨텍스트: 이선호/"*"자동제작"*.md | tail -1
```
그 리포트를 열어 확인:
- Figma 시안 링크(node-id) + CdBd 에디터 링크(/editor/{id})가 **실제 URL**
- 검수 로그에 단계별 통과/수정 기록
- state.json: 선택 slug가 queue에서 빠지고 completed에 추가, recent_moods에 무드 추가
Expected: 위 모두 충족. 링크 클릭 시 실제 Figma 시안·CdBd 에디터 열림.

- [ ] **Step 5: 게이트 — 사용자 검수**

라이브 산출 템플릿 1건을 사용자가 직접 검수(링크 2개 열어 ⚠️·⭐ 확인). 품질이 기준 미달이면 → SKILL.md/critic-checklists.md 보강 후 Task 3·4 재방문. 합격이면 정식 가동.

- [ ] **Step 6: 정식 가동 확인 + 커밋**

Run:
```bash
launchctl list | grep cdbd
cp ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json" "$HOME/.config/cdbd/automation/state.json"  # 큐 원복(라이브 1건 소비분 복구 여부는 사용자 판단)
```
Expected: launchd 등록 유지 → 다음 20:00부터 자동. 끄려면 `launchctl unload ~/Library/LaunchAgents/in.cdbd.daily-template.plist`.

```bash
git add ".claude/skills/cdbd-daily-orchestrator/runtime/state.seed.json"
git commit -m "feat(orchestrator): 라이브 실증 + 정식 가동"
```

---

## Self-Review (작성자 점검 결과)

**1. Spec coverage** — 설계 섹션 대비:
- 등장 역할(매니저·담당자·검수자) → Task 3 SKILL.md ✅
- 하루 흐름(자가진단→주제선택→1~5단계+검수→정리→리포트) → Task 3 §1~5 ✅
- 검수 기준(2~5단계 체크리스트) → Task 4 critic-checklists ✅
- 실패=부분완성+리포트, retry 2 → Task 3 §3 + Global Constraints ✅
- 아침 리포트(링크 2개·⭐·후보규칙·경고) → Task 4 report-template + Task 3 §5 ✅
- 안전장치: 자가진단/재로그인 → Task 2+Task 3 §1 ✅ · 무드 회피 → Task 3 §2 ✅ · 청소 → Task 3 §4 ✅ · 큐 경고 → Task 7 Step1 ✅ · 적체 정지 → Task 7 Step2 ✅
- launchd 등록 → Task 6 ✅ · Flow 제외 → Global Constraints + critic 3단계 ✅
- 인증 만료 특성 표 → preflight(저비용)+매니저 라이브체크로 커버 ✅

**2. Placeholder scan** — 스크립트·체크리스트·템플릿은 실제 내용 포함. 리포트 템플릿의 `{slug}` 등은 런타임 치환 자리(플레이스홀더 금지 대상 아님). "구현 시 결정" 6항목은 Global Constraints에서 확정값으로 고정됨(미해결 없음).

**3. Type consistency** — state.json 키(`queue`,`retry_queue`,`recent_moods`,`completed`,`params.*`,`last_run`,`paused`)가 Task 1 정의 ↔ Task 3 사용 ↔ Task 7 jq 조작에서 동일. 스크립트 경로(`~/.config/cdbd/automation/*`)·plist Label(`in.cdbd.daily-template`)이 Task 2·5·6에서 일치.

**열린 리스크(코드 아닌 운영):** 헤드리스 `claude -p`에서 Figma 데스크탑 MCP 연결 신뢰성은 Task 7 Step3 라이브에서 최초 실증 — 만약 헤드리스에서 MCP가 안 붙으면, run-daily를 GUI 로그인 세션에 띄우는 방식(예: launchd `LimitLoadToSessionType Aqua`)으로 보강 필요. 이 분기는 Task 7에서 관찰 후 결정.
