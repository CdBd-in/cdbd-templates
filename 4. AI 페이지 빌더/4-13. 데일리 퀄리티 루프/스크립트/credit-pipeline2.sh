#!/bin/bash
# 재시도 파이프라인(즉시 실행): 콘솔 세션 복구 → L4r(PDF 첨부·미입력) → L1c(설명만·미입력) → 토큰 읽기
S="$(cd "$(dirname "$0")" && pwd)"; AR="$S/../아카이브/$(date +%Y-%m-%d)/credit"; mkdir -p "$AR"
B="$HOME/.claude/skills/gstack/browse/dist/browse"
# 탭 정리: 1=빌더, 2=콘솔
$B tab 1 >/dev/null 2>&1; $B goto "https://cdbd-client-git-ai-makevu-s-team.vercel.app/ai/create" >/dev/null 2>&1; sleep 4
for t in 2 3 4 5; do $B closetab $t >/dev/null 2>&1; done
$B newtab "https://platform.claude.com/usage" >/dev/null 2>&1; sleep 3
export BUILDER_TAB=1 CONSOLE_TAB=$($B tabs 2>/dev/null | grep -oE '\[[0-9]+\] Usage|\[[0-9]+\] [^—]*platform' | grep -oE '[0-9]+' | head -1); [ -z "$CONSOLE_TAB" ] && CONSOLE_TAB=2
$B tab $CONSOLE_TAB >/dev/null 2>&1
if $B text 2>/dev/null | sed -n '2p' | grep -q "Continue with Google"; then $B cookie-import-browser chrome --profile "Profile 11" --all 2>&1 | tail -1; $B goto "https://platform.claude.com/usage" >/dev/null 2>&1; sleep 8; fi
echo "tabs: builder=$BUILDER_TAB console=$CONSOLE_TAB · $($B text 2>/dev/null | sed -n '2p' | grep -oE '크레딧\$[0-9.]+|Continue with Google' | head -1)"
T0=$(date -u +%Y-%m-%dT%H:%M:00Z); echo "$T0" > "$AR/T0-retry.txt"
rd(){ "$S/usage-read.sh" "$1" "$T0" | tee -a "$AR/retry-reads.txt"; }
rd r00-baseline
export ATTACH="$S/../아카이브/2026-10-21/credit/wanted-383387.pdf" FILL=0
STAGE=1 "$S/credit-run.sh" L4r "개발자 채용 공고 페이지 제작. 공고 내용은 원티드에 올린 것 그대로. 공고 PDF 첨부." ; rd r01-L4r-draft1
STAGE=2 "$S/credit-run.sh" L4r ; rd r02-L4r-3drafts
STAGE=3 "$S/credit-run.sh" L4r ; rd r03-L4r-editor
unset ATTACH
STAGE=1 "$S/credit-run.sh" L1c "요가 원데이 클래스 모집 페이지. 성수동 요가 스튜디오에서 매주 토요일 오전 10시 초보자 대상 90분 수업. 참가비 3만원, 매트 제공. 인스타그램 DM이나 전화로 예약." ; rd r04-L1c-draft1
STAGE=2 "$S/credit-run.sh" L1c ; rd r05-L1c-3drafts
STAGE=3 "$S/credit-run.sh" L1c ; rd r06-L1c-editor
echo "DONE $(date +%H:%M)"
