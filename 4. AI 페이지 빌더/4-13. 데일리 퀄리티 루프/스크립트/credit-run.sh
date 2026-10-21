#!/bin/bash
# 크레딧 측정용 단계 실행 — 사용: STAGE=1|2|3 credit-run.sh <사례ID> "<설명>"  (빌더 = 1번 탭 로그인 전제)
# STAGE 1: 설명 입력 → 확인 화면들 → 첫 시안 완료에서 정지  / STAGE 2: 시작하기 → 내용 채우기 → 3안 완료에서 정지 / STAGE 3: 시안A → 무드 → 에디터 도착
B="$HOME/.claude/skills/gstack/browse/dist/browse"
ID="$1"; DESC="$2"
AR="/Users/leesunho/Documents/GitHub/design/cdbd-templates/4. AI 페이지 빌더/4-13. 데일리 퀄리티 루프/아카이브/$(date +%Y-%m-%d)/credit"; mkdir -p "$AR"
LOG="$AR/$ID-log.txt"
log(){ echo "[$(date -u +%H:%M:%S)Z] $*" | tee -a "$LOG"; }
ref(){ $B snapshot -i 2>/dev/null | grep -E "\[button\] \"$1\"" | grep -v disabled | head -1 | grep -oE '@e[0-9]+' | head -1; }
head2(){ $B text 2>/dev/null | sed -n '2p' | cut -c1-${1:-150}; }
pick(){ # 라벨·화면 제목 키워드로 답 고르기
  case "$1 $2" in
    *이메일*) echo "recruit@healingpaper.com";; *연락처*|*전화*|*휴대폰*|*"값"*) echo "010-1234-5678";;
    *주소*|*장소*) echo "서울 강남구 테헤란로 142 아크플레이스 15층";; *호스트*|*담당*|*이름*) echo "김하나";;
    *"제목 위"*|*eyebrow*) echo "힐링페이퍼 채용";; *제목*) echo "웹 프론트엔드 개발자 채용";;
    *가격*|*금액*|*비용*) echo "연봉 협의";; *일시*|*날짜*|*기간*) echo "상시 채용";;
    *) echo "디자인 시스템을 함께 만들 웹 프론트엔드 개발자를 모십니다. 자세한 내용은 아래 공고를 확인해 주세요.";;
  esac; }
fill_screen(){ # 빈 textbox만 채움 (스냅샷 순서 = DOM 순서 가정)
  local H="$1" n=0
  local REFS; REFS=$($B snapshot -i 2>/dev/null | grep '\[textbox\]' | sed -E 's/^ *(@e[0-9]+) \[textbox\] ?"?([^"]*)"?.*/\1|\2/')
  local VALS; VALS=$($B js "[...document.querySelectorAll('input:not([type=hidden]):not([type=file]):not([type=checkbox]):not([type=radio]),textarea')].map(e=>e.value.length).join(',')" 2>/dev/null)
  local i=0; IFS=',' read -ra V <<< "$VALS"
  while IFS='|' read -r r name; do
    [ -z "$r" ] && continue
    if [ "${V[$i]:-0}" = "0" ] && [ $n -lt 6 ]; then A=$(pick "$name" "$H"); $B fill "$r" "$A" >/dev/null 2>&1; n=$((n+1)); log "   채움[$name]=$A"; fi
    i=$((i+1))
  done <<< "$REFS"
  sleep 1; }
$B tab 1 >/dev/null 2>&1

if [ "$STAGE" = "1" ]; then
  log "STAGE1 시작"
  $B goto "https://cdbd-client-git-ai-makevu-s-team.vercel.app/ai/create" >/dev/null 2>&1; sleep 5
  TB=$($B snapshot -i 2>/dev/null | grep -E '\[textbox\]' | head -1 | grep -oE '@e[0-9]+' | head -1)
  [ -z "$TB" ] && { log "FAIL: 입력칸 없음 ($($B url))"; exit 1; }
  if [ -n "$ATTACH" ]; then $B upload "input[type=file]" "$ATTACH" >/dev/null 2>&1; sleep 4; log "첨부: $(basename "$ATTACH") → $($B text 2>/dev/null | sed -n '2p' | grep -oE '[^ ]*\.pdf' | head -1)"; fi
  $B fill "$TB" "$DESC" >/dev/null 2>&1; sleep 1
  log "설명 전송"; $B click "$(ref '보내기')" >/dev/null 2>&1; sleep 6
  log "설명 확인: $(head2 200)"
  for i in $(seq 1 10); do
    H=$(head2 200)
    case "$H" in *"시안 제작 중"*|*"첫 번째 시안"*) break;; esac
    case "$H" in *"원페이지"*|*"멀티페이지"*) log "유형: $(echo "$H" | cut -c1-80)";; esac
    R=$(ref '다음'); [ -z "$R" ] && { sleep 3; R=$(ref '다음'); }
    [ -z "$R" ] && { log "STOP: 다음 버튼 없음 — $H"; break; }
    $B click "$R" >/dev/null 2>&1; sleep 5
  done
  log "1안 생성 시작(폴링)"
  for i in $(seq 1 18); do [ -n "$(ref '시작하기')" ] && break; sleep 10; done
  log "1안 완료 ← ② 측정 지점"
  $B screenshot "$AR/$ID-draft1.png" --viewport >/dev/null 2>&1
fi

if [ "$STAGE" = "2" ]; then
  log "STAGE2 시작: 시작하기 클릭"
  $B click "$(ref '시작하기')" >/dev/null 2>&1; sleep 4
  PREV=""; REP=0
  for i in $(seq 1 25); do
    R=$(ref '확인했어요'); [ -n "$R" ] && break
    H=$(head2 120); log "Q$i: $H"
    if [ "$H" = "$PREV" ]; then REP=$((REP+1)); else REP=0; fi; PREV="$H"
    if [ "$REP" -ge 2 ]; then
      D=$($B snapshot -i 2>/dev/null | grep -E '\[button\] "항목 지우기"' | head -1 | grep -oE '@e[0-9]+')
      log "STUCK → 항목 지우기 우회"; [ -n "$D" ] && { $B click "$D" >/dev/null 2>&1; sleep 1.5; }; REP=0
    fi
    [ "$FILL" = "1" ] && fill_screen "$H"
    R=$(ref '다음'); [ -z "$R" ] && R=$(ref '이건 없어요')
    [ -z "$R" ] && { sleep 3; R=$(ref '다음'); [ -z "$R" ] && R=$(ref '이건 없어요'); }
    [ -z "$R" ] && { log "STOP: 채우기 버튼 없음"; break; }
    $B click "$R" >/dev/null 2>&1; sleep 3
  done
  log "채우기 끝 → 마지막 확인: $(head2 200)"
  $B screenshot "$AR/$ID-final-check.png" --viewport >/dev/null 2>&1
  $B click "$(ref '확인했어요')" >/dev/null 2>&1
  log "3안 생성 시작(폴링)"
  for i in $(seq 1 18); do sleep 10; [ -n "$(ref '3안 재생성')" ] && break; done
  $B snapshot -i 2>/dev/null | grep -E '\[button\] "시안 [ABC]' | sed 's/^ *@e[0-9]* \[button\] //' > "$AR/$ID-3drafts.txt"
  log "3안 완료 ($(wc -l < "$AR/$ID-3drafts.txt" | tr -d ' ')안) ← ③ 측정 지점"
  $B screenshot "$AR/$ID-3drafts.png" --viewport >/dev/null 2>&1
fi

if [ "$STAGE" = "3" ]; then
  log "STAGE3 시작: 시안A → 무드 → 에디터"
  A=$($B snapshot -i 2>/dev/null | grep -E '\[button\] "시안 A' | grep -oE '@e[0-9]+' | head -1)
  $B click "$A" >/dev/null 2>&1; sleep 2; $B click "$(ref '다음')" >/dev/null 2>&1; sleep 5
  log "무드: $(head2 100)"; $B click "$(ref '다음')" >/dev/null 2>&1
  for i in $(seq 1 18); do sleep 10; case "$($B url 2>/dev/null)" in *editor*) break;; esac; done
  log "에디터 도착: $($B url) ← ④ 측정 지점"
fi
