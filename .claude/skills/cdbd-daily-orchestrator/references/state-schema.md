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
승인 적체(approval_backlog)는 저장하지 않고 **매 실행 시작 시 재계산**(SKILL.md §1): `컨텍스트: 이선호/` 의 `자동제작` 리포트 중 frontmatter에 `검수: 완료`가 없는 노트 수.
