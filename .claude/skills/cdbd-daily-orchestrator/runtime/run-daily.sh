#!/bin/zsh
set -u
DIR="$HOME/.config/cdbd/automation"
VAULT="/Users/designer/Documents/GitHub/design/cdbd-templates"
CLAUDE="/Users/designer/.local/bin/claude"
mkdir -p "$DIR/logs"
LOG="$DIR/logs/$(date +%F).log"
exec >>"$LOG" 2>&1

echo "=== run $(date '+%F %T') dryrun=${CDBD_ORCH_DRYRUN:-0} ==="

# 작업 동안(최대 6시간) 맥이 잠들지 않게 — preflight 네트워크 재시도 대기 중에도 잠들지 않도록 먼저 시작
/usr/bin/caffeinate -i -t 21600 &
CAF=$!

if ! "$DIR/preflight.sh"; then
  "$DIR/notify.sh" "자가진단 실패 — 오늘 제작 중단. 로그: $LOG"
  echo "preflight failed; abort"; kill $CAF 2>/dev/null; exit 1
fi

cd "$VAULT" || { echo "vault cd 실패"; kill $CAF 2>/dev/null; exit 1; }
PROMPT="당신은 CdBd 일일 템플릿 매니저입니다. cdbd-daily-orchestrator 스킬을 호출해 오늘의 무인 제작을 1회 실행하세요. 환경변수 CDBD_ORCH_DRYRUN 을 존중하세요(=1이면 드라이런)."

CDBD_ORCH_DRYRUN="${CDBD_ORCH_DRYRUN:-0}" "$CLAUDE" -p "$PROMPT" --dangerously-skip-permissions
RC=$?

kill $CAF 2>/dev/null
echo "=== done rc=$RC $(date '+%F %T') ==="
exit $RC
